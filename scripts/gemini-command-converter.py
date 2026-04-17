#!/usr/bin/env python3
"""
Convert Gemini CLI command files between TOML and Markdown front matter.

Supported mappings:
- `.toml` -> `.md`: all non-`prompt` TOML fields become front matter, `prompt`
  becomes the Markdown body.
- `.md` -> `.toml`: front matter becomes TOML fields, Markdown body becomes
  `prompt`.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).parent.resolve()

try:
    import yaml  # type: ignore
except ModuleNotFoundError:
    yaml = None


class ConversionError(ValueError):
    """Raised when a source file cannot be converted safely."""


@dataclass(frozen=True)
class GeminiCommand:
    metadata: dict[str, Any]
    prompt: str


class FrontmatterCodec:
    @staticmethod
    def parse_document(text: str) -> GeminiCommand:
        if not text.startswith("---"):
            raise ConversionError("Markdown file is missing YAML front matter.")

        lines = text.splitlines(keepends=True)
        if not lines or lines[0].strip() != "---":
            raise ConversionError("Markdown front matter is malformed.")

        closing_index = None
        for index in range(1, len(lines)):
            if lines[index].strip() == "---":
                closing_index = index
                break

        if closing_index is None:
            raise ConversionError("Markdown front matter is malformed.")

        frontmatter_text = "".join(lines[1:closing_index]).strip()
        body = "".join(lines[closing_index + 1 :])
        if body.startswith("\n"):
            body = body[1:]

        metadata = FrontmatterCodec.parse_frontmatter(frontmatter_text)
        if not isinstance(metadata, dict):
            raise ConversionError("Markdown front matter must parse to an object.")

        return GeminiCommand(metadata=metadata, prompt=body.rstrip("\n"))

    @staticmethod
    def parse_frontmatter(frontmatter_text: str) -> dict[str, Any]:
        if yaml is not None:
            parsed = yaml.safe_load(frontmatter_text) or {}
            if not isinstance(parsed, dict):
                raise ConversionError("YAML front matter must be a mapping.")
            return parsed

        return FrontmatterCodec._parse_simple_yaml(frontmatter_text)

    @staticmethod
    def dump_document(command: GeminiCommand) -> str:
        frontmatter = FrontmatterCodec.dump_frontmatter(command.metadata)
        body = command.prompt.rstrip("\n")
        return f"---\n{frontmatter}\n---\n\n{body}\n"

    @staticmethod
    def dump_frontmatter(metadata: dict[str, Any]) -> str:
        if yaml is not None:
            return yaml.safe_dump(
                metadata,
                sort_keys=False,
                allow_unicode=False,
                default_flow_style=False,
            ).strip()

        return FrontmatterCodec._dump_simple_yaml(metadata)

    @staticmethod
    def _parse_simple_yaml(frontmatter_text: str) -> dict[str, Any]:
        lines = frontmatter_text.splitlines()
        result: dict[str, Any] = {}
        index = 0

        while index < len(lines):
            raw_line = lines[index]
            stripped = raw_line.strip()

            if not stripped or stripped.startswith("#"):
                index += 1
                continue

            if raw_line.startswith((" ", "\t")):
                raise ConversionError(
                    "Indented front matter requires PyYAML; install pyyaml for this file."
                )

            if ":" not in raw_line:
                raise ConversionError(f"Invalid front matter line: {raw_line}")

            key, raw_value = raw_line.split(":", 1)
            key = key.strip()
            value = raw_value.strip()

            if value in {"|", ">"}:
                block_lines: list[str] = []
                index += 1
                while index < len(lines):
                    block_line = lines[index]
                    if block_line.startswith((" ", "\t")):
                        block_lines.append(block_line[1:] if block_line else "")
                        index += 1
                        continue
                    break
                result[key] = "\n".join(block_lines).rstrip("\n")
                continue

            if value == "":
                list_values: list[Any] = []
                probe = index + 1
                while probe < len(lines):
                    probe_line = lines[probe]
                    probe_stripped = probe_line.strip()
                    if not probe_stripped or probe_stripped.startswith("#"):
                        probe += 1
                        continue
                    if probe_line.startswith((" ", "\t")) and probe_stripped.startswith("- "):
                        list_values.append(
                            FrontmatterCodec._parse_yaml_scalar(probe_stripped[2:].strip())
                        )
                        probe += 1
                        continue
                    break

                if list_values:
                    result[key] = list_values
                    index = probe
                    continue

                result[key] = ""
                index += 1
                continue

            result[key] = FrontmatterCodec._parse_yaml_scalar(value)
            index += 1

        return result

    @staticmethod
    def _parse_yaml_scalar(value: str) -> Any:
        lowered = value.lower()
        if lowered in {"true", "false"}:
            return lowered == "true"
        if lowered in {"null", "~"}:
            return None
        if value.startswith(("[", "{")):
            try:
                return json.loads(value)
            except json.JSONDecodeError as exc:
                raise ConversionError(f"Unsupported inline YAML value: {value}") from exc
        if value.startswith('"') and value.endswith('"'):
            return json.loads(value)
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]

        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            pass

        return value

    @staticmethod
    def _dump_simple_yaml(metadata: dict[str, Any]) -> str:
        lines: list[str] = []
        for key, value in metadata.items():
            lines.extend(FrontmatterCodec._dump_yaml_entry(key, value))
        return "\n".join(lines)

    @staticmethod
    def _dump_yaml_entry(key: str, value: Any) -> list[str]:
        if isinstance(value, list):
            if not value:
                return [f"{key}: []"]
            lines = [f"{key}:"]
            for item in value:
                lines.append(f"  - {FrontmatterCodec._dump_yaml_scalar(item)}")
            return lines

        return [f"{key}: {FrontmatterCodec._dump_yaml_scalar(value)}"]

    @staticmethod
    def _dump_yaml_scalar(value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)

        text = str(value)
        if text == "" or text != text.strip() or any(
            ch in text for ch in [":", "#", "[", "]", "{", "}", "\n"]
        ):
            return json.dumps(text, ensure_ascii=False)
        return text


class GeminiTomlCodec:
    BODY_KEY = "prompt"

    @staticmethod
    def parse_document(text: str) -> GeminiCommand:
        try:
            data = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            raise ConversionError(f"Invalid TOML: {exc}") from exc

        if GeminiTomlCodec.BODY_KEY not in data:
            raise ConversionError("Gemini TOML command is missing a `prompt` field.")

        prompt = data[GeminiTomlCodec.BODY_KEY]
        if not isinstance(prompt, str):
            raise ConversionError("The `prompt` field must be a string.")

        metadata = {key: value for key, value in data.items() if key != GeminiTomlCodec.BODY_KEY}
        return GeminiCommand(metadata=metadata, prompt=prompt.rstrip("\n"))

    @staticmethod
    def dump_document(command: GeminiCommand) -> str:
        lines: list[str] = []
        lines.extend(TomlWriter.dump_mapping(command.metadata))
        if lines:
            lines.append("")
        lines.append(f"{GeminiTomlCodec.BODY_KEY} = {TomlWriter.dump_string(command.prompt, multiline=True)}")
        return "\n".join(lines) + "\n"


class TomlWriter:
    @staticmethod
    def dump_mapping(data: dict[str, Any], prefix: str | None = None) -> list[str]:
        scalars: list[tuple[str, Any]] = []
        tables: list[tuple[str, dict[str, Any]]] = []

        for key, value in data.items():
            TomlWriter._validate_key(key)
            if isinstance(value, dict):
                tables.append((key, value))
            else:
                scalars.append((key, value))

        lines = [f"{key} = {TomlWriter.dump_value(value)}" for key, value in scalars]

        for key, value in tables:
            table_name = key if prefix is None else f"{prefix}.{key}"
            if lines:
                lines.append("")
            lines.append(f"[{table_name}]")
            nested_lines = TomlWriter.dump_mapping(value, prefix=table_name)
            lines.extend(nested_lines)

        return lines

    @staticmethod
    def dump_value(value: Any) -> str:
        if value is None:
            raise ConversionError("TOML does not support null values.")
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            return TomlWriter.dump_string(value)
        if isinstance(value, list):
            return "[" + ", ".join(TomlWriter.dump_value(item) for item in value) + "]"
        raise ConversionError(f"Unsupported TOML value type: {type(value).__name__}")

    @staticmethod
    def dump_string(value: str, multiline: bool = False) -> str:
        if multiline or "\n" in value:
            trimmed = value.rstrip("\n")
            if "'''" not in trimmed:
                return "'''\n" + trimmed + "\n'''"
        return json.dumps(value, ensure_ascii=False)

    @staticmethod
    def _validate_key(key: str) -> None:
        if not key or any(char.isspace() for char in key):
            raise ConversionError(f"Unsupported TOML key: {key!r}")


class Converter:
    SUPPORTED_EXTENSIONS = {".toml", ".md"}

    def convert_path(self, source: Path, output: Path | None = None, to_format: str | None = None) -> list[Path]:
        source = source.resolve()
        if source.is_dir():
            target_format = self._resolve_directory_target_format(to_format)
            return self._convert_directory(source, output, target_format)

        converted_text, destination = self.convert_file(source, output=output, to_format=to_format)
        destination.write_text(converted_text, encoding="utf-8")
        return [destination]

    def convert_file(
        self,
        source: Path,
        output: Path | None = None,
        to_format: str | None = None,
    ) -> tuple[str, Path]:
        source = source.resolve()
        source_format = self._resolve_source_format(source)
        target_format = self._resolve_target_format(source_format, to_format)
        command = self._load_command(source, source_format)
        converted_text = self._dump_command(command, target_format)
        destination = self._resolve_output_path(source, output, target_format)
        return converted_text, destination

    def _convert_directory(self, source_dir: Path, output_dir: Path | None, target_format: str) -> list[Path]:
        if output_dir is None:
            raise ConversionError("Directory conversion requires --output.")

        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        source_extension = ".toml" if target_format == "md" else ".md"
        sources = sorted(path for path in source_dir.rglob(f"*{source_extension}") if path.is_file())
        if not sources:
            raise ConversionError(f"No {source_extension} files found under {source_dir}.")

        created_paths: list[Path] = []
        for source in sources:
            relative = source.relative_to(source_dir).with_suffix(f".{target_format}")
            destination = output_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            converted_text, _ = self.convert_file(source, output=destination, to_format=target_format)
            destination.write_text(converted_text, encoding="utf-8")
            created_paths.append(destination)

        return created_paths

    def _load_command(self, source: Path, source_format: str) -> GeminiCommand:
        text = source.read_text(encoding="utf-8")
        if source_format == "toml":
            return GeminiTomlCodec.parse_document(text)
        return FrontmatterCodec.parse_document(text)

    def _dump_command(self, command: GeminiCommand, target_format: str) -> str:
        if target_format == "md":
            return FrontmatterCodec.dump_document(command)
        return GeminiTomlCodec.dump_document(command)

    def _resolve_source_format(self, source: Path) -> str:
        suffix = source.suffix.lower()
        if suffix not in self.SUPPORTED_EXTENSIONS:
            raise ConversionError(f"Unsupported file type: {source}")
        return suffix[1:]

    def _resolve_target_format(self, source_format: str, to_format: str | None) -> str:
        if to_format is None:
            return "md" if source_format == "toml" else "toml"
        if to_format == source_format:
            raise ConversionError("Source and target formats are the same.")
        return to_format

    def _resolve_directory_target_format(self, to_format: str | None) -> str:
        if to_format not in {"md", "toml"}:
            raise ConversionError("Directory conversion requires --to md or --to toml.")
        return to_format

    def _resolve_output_path(self, source: Path, output: Path | None, target_format: str) -> Path:
        if output is None:
            return source.with_suffix(f".{target_format}")
        if output.exists() and output.is_dir():
            return (output / source.with_suffix(f".{target_format}").name).resolve()
        return output.resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert Gemini CLI command files between TOML and Markdown front matter."
    )
    parser.add_argument("source", help="Path to a .toml/.md file or a directory tree to convert.")
    parser.add_argument(
        "-o",
        "--output",
        help="Output file or directory. Defaults to changing the source suffix in place.",
    )
    parser.add_argument(
        "--to",
        choices=["md", "toml"],
        help="Force the output format. Required for directory conversions.",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print converted content instead of writing a file. File inputs only.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    source = Path(args.source)
    output = Path(args.output).expanduser() if args.output else None
    converter = Converter()

    try:
        if args.stdout:
            if source.is_dir():
                raise ConversionError("--stdout only supports single-file conversions.")
            converted_text, _ = converter.convert_file(source, output=output, to_format=args.to)
            sys.stdout.write(converted_text)
            return 0

        created_paths = converter.convert_path(source, output=output, to_format=args.to)
    except ConversionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for path in created_paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

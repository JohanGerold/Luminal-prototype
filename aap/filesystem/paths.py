import stat
from pathlib import Path


class ToolError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def reject_links(path):
    if path.exists() or path.is_symlink():
        info = path.lstat()
        if path.is_symlink() or path.is_junction() or getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ToolError("BOUNDARY_REJECTED", "Linked paths are not permitted.")
        if path.is_file() and info.st_nlink > 1:
            raise ToolError("BOUNDARY_REJECTED", "Hard-linked files are not permitted.")


def safe_path(root: Path, relative: str, allow_root=False):
    if not isinstance(relative, str) or not relative or len(relative) > 512:
        raise ToolError("INVALID_ARGUMENTS", "Expected a bounded relative path.")
    raw = relative.replace("\\", "/")
    pieces = raw.split("/")
    devices = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}
    if raw.startswith("/") or ":" in raw or ".." in pieces or any(ord(c) < 32 for c in raw):
        raise ToolError("BOUNDARY_REJECTED", "Only workspace-relative paths are permitted.")
    for piece in pieces:
        if piece not in ("", ".") and (piece.endswith((".", " ")) or piece.split(".")[0].upper() in devices):
            raise ToolError("BOUNDARY_REJECTED", "Ambiguous Windows paths are not permitted.")
    if ".aap-demo-owned" in pieces:
        raise ToolError("BOUNDARY_REJECTED", "Workspace metadata is protected.")
    candidate = root.joinpath(*[p for p in pieces if p not in ("", ".")])
    reject_links(root)
    for parent in candidate.parents:
        if parent == root:
            break
        if parent.is_relative_to(root):
            reject_links(parent)
    reject_links(candidate)
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root.resolve()) or (resolved == root.resolve() and not allow_root):
        raise ToolError("BOUNDARY_REJECTED", "Path is outside the permitted workspace or names its root.")
    return candidate

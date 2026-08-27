"""Compiles locale/*/LC_MESSAGES/django.po into .mo catalogs.

Stands in for `django-admin compilemessages`, which needs the GNU gettext
`msgfmt` binary — not available on every machine (e.g. plain Windows without
gettext installed). After hand-editing a .po file, run:

    python scripts/compile_mo.py

to regenerate the matching .mo file. If gettext is installed, `django-admin
compilemessages` works fine too and produces the same result.
"""

import glob
import os
import struct

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _unquote(line):
    line = line.strip()
    assert line.startswith('"') and line.endswith('"'), line
    line = line[1:-1]
    return line.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")


def parse_po(po_path):
    messages = {}
    msgid = None
    msgstr = None
    mode = None
    with open(po_path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("msgid "):
                if msgid is not None:
                    messages[msgid] = msgstr or ""
                msgid = _unquote(line[len("msgid ") :])
                msgstr = None
                mode = "id"
            elif line.startswith("msgstr "):
                msgstr = _unquote(line[len("msgstr ") :])
                mode = "str"
            elif line.startswith('"'):
                piece = _unquote(line)
                if mode == "id":
                    msgid += piece
                elif mode == "str":
                    msgstr += piece
        if msgid is not None:
            messages[msgid] = msgstr or ""
    return messages


def compile_mo(messages, mo_path):
    """Writes the GNU MO binary format directly (see the format spec at
    https://www.gnu.org/software/gettext/manual/html_node/MO-Files.html)."""
    keys = sorted(messages.keys())
    ids = b""
    strs = b""
    offsets = []
    for k in keys:
        k_enc = k.encode("utf-8")
        v_enc = messages[k].encode("utf-8")
        offsets.append((len(ids), len(k_enc), len(strs), len(v_enc)))
        ids += k_enc + b"\x00"
        strs += v_enc + b"\x00"

    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)

    header = struct.pack(
        "Iiiiiii",
        0x950412DE,
        0,
        len(keys),
        7 * 4,
        7 * 4 + len(keys) * 8,
        0,
        0,
    )
    body = b""
    for o1, l1, o2, l2 in offsets:
        body += struct.pack("Ii", l1, o1 + keystart)
    for o1, l1, o2, l2 in offsets:
        body += struct.pack("Ii", l2, o2 + valuestart)

    with open(mo_path, "wb") as f:
        f.write(header + body + ids + strs)


def main():
    po_files = glob.glob(os.path.join(BASE_DIR, "locale", "*", "LC_MESSAGES", "*.po"))
    for po_path in po_files:
        mo_path = po_path[:-3] + ".mo"
        messages = parse_po(po_path)
        compile_mo(messages, mo_path)
        print(f"compiled {mo_path} ({len(messages)} entries)")


if __name__ == "__main__":
    main()

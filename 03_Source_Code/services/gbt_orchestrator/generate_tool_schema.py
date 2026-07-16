import ast, json, sys

SRC = "/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/services/mcp_server/hci_mcp_server.py"

TYPE_MAP = {
    "str": "string", "int": "integer", "float": "number",
    "bool": "boolean", "dict": "object", "list": "array",
}

def annotation_to_type(ann):
    if ann is None:
        return "string"
    if isinstance(ann, ast.Name):
        return TYPE_MAP.get(ann.id, "string")
    if isinstance(ann, ast.Subscript):
        # e.g. list[str], dict[str, Any], Optional[str]
        base = ann.value.id if isinstance(ann.value, ast.Name) else None
        return TYPE_MAP.get(base, "string")
    if isinstance(ann, ast.Constant):
        return "string"
    return "string"

def default_repr(node):
    if node is None:
        return None
    try:
        return ast.literal_eval(node)
    except Exception:
        return None

tree = ast.parse(open(SRC).read())
tools = []

for node in ast.walk(tree):
    if not isinstance(node, ast.FunctionDef):
        continue
    is_tool = any(
        (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == "tool")
        or (isinstance(d, ast.Attribute) and d.attr == "tool")
        for d in node.decorator_list
    )
    if not is_tool:
        continue

    docstring = ast.get_docstring(node) or ""
    # first line/paragraph as short description
    desc = docstring.strip().split("\n\n")[0].replace("\n", " ").strip()
    if not desc:
        desc = node.name

    args = node.args
    defaults = [None] * (len(args.args) - len(args.defaults)) + list(args.defaults)
    properties = {}
    required = []
    for arg, default in zip(args.args, defaults):
        if arg.arg == "self":
            continue
        ptype = annotation_to_type(arg.annotation)
        prop = {"type": ptype}
        properties[arg.arg] = prop
        if default is None:
            required.append(arg.arg)
        else:
            dval = default_repr(default)
            if dval is not None:
                prop["default"] = dval

    tools.append({
        "type": "function",
        "function": {
            "name": node.name,
            "description": desc[:1024],
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    })

OUT = "/Users/buckadams/HCI_AI_Operating_System/03_Source_Code/services/gbt_orchestrator/assistant_tools.json"
json.dump(tools, open(OUT, "w"), indent=2)
print(f"Wrote {len(tools)} tool definitions to {OUT}")

"""Генерация автодополнения bash/zsh/fish прямо из argparse-парсера,
поэтому списки команд и флагов никогда не расходятся с реальными."""
from __future__ import annotations

import argparse
from typing import Dict, List


def _subparsers(parser: argparse.ArgumentParser):
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action
    return None


def collect(parser: argparse.ArgumentParser) -> Dict:
    sub = _subparsers(parser)
    helps: Dict[str, str] = {}
    for act in sub._choices_actions:
        helps[act.dest] = act.help or ""
    commands: Dict[str, Dict] = {}
    for name, sp in sub.choices.items():
        primary = next((d for d in helps if sub.choices[d] is sp), name)
        opts, positional = [], []
        for act in sp._actions:
            if isinstance(act, argparse._HelpAction):
                continue
            if act.option_strings:
                opts.append({
                    "flags": list(act.option_strings),
                    "help": act.help or "",
                    "takes_value": act.nargs != 0,
                    "choices": list(act.choices) if act.choices else [],
                })
            elif act.choices:
                positional.append(list(act.choices))
        commands[name] = {"help": helps.get(primary, ""), "options": opts,
                          "positional": positional}
    global_opts = []
    for act in parser._actions:
        if act.option_strings and not isinstance(act, argparse._SubParsersAction):
            global_opts.extend(act.option_strings)
    return {"commands": commands, "global": global_opts}


def _clean(text: str) -> str:
    for ch in "[]:'\"\\`$":
        text = text.replace(ch, " ")
    return " ".join(text.split())


def bash(parser) -> str:
    data = collect(parser)
    cmds = list(data["commands"])
    glob = [f for f in data["global"] if f not in ("-h", "--help")]
    choice_cases = {}
    for info in data["commands"].values():
        for opt in info["options"]:
            if opt["choices"]:
                for flag in opt["flags"]:
                    choice_cases[flag] = opt["choices"]
    out = ["# dpa bash completion (generated)", "_dpa() {",
           "    local cur prev cmd i", "    COMPREPLY=()",
           '    cur="${COMP_WORDS[COMP_CWORD]}"',
           '    prev="${COMP_WORDS[COMP_CWORD-1]}"', '    cmd=""',
           "    for ((i=1; i<COMP_CWORD; i++)); do",
           '        case "${COMP_WORDS[i]}" in',
           "            %s) cmd=\"${COMP_WORDS[i]}\"; break ;;" % "|".join(cmds),
           "        esac", "    done",
           '    if [[ -z "$cmd" ]]; then',
           '        COMPREPLY=( $(compgen -W "%s %s" -- "$cur") )'
           % (" ".join(cmds), " ".join(glob)),
           "        return 0", "    fi"]
    if choice_cases:
        out.append('    case "$prev" in')
        for flag, vals in choice_cases.items():
            out.append('        %s) COMPREPLY=( $(compgen -W "%s" -- "$cur") ); return 0 ;;'
                       % (flag, " ".join(vals)))
        out.append("    esac")
    out.append('    case "$cmd" in')
    for name, info in data["commands"].items():
        words: List[str] = []
        for choices in info["positional"]:
            words.extend(choices)
        for opt in info["options"]:
            words.extend(opt["flags"])
        words = list(dict.fromkeys(words + glob))
        out.append('        %s) COMPREPLY=( $(compgen -W "%s" -- "$cur") ) ;;'
                   % (name, " ".join(words)))
    out += ["    esac", "}", "complete -F _dpa dpa", ""]
    return "\n".join(out)


def zsh(parser) -> str:
    data = collect(parser)
    out = ["# dpa zsh completion (generated)",
           "(( $+functions[compdef] )) || { autoload -Uz compinit && compinit; }",
           "_dpa() {", "    local -a commands", "    commands=("]
    for name, info in data["commands"].items():
        out.append("        '%s:%s'" % (name, _clean(info["help"])))
    out += ["    )", "    if (( CURRENT == 2 )); then",
            "        _describe -t commands 'dpa command' commands", "        return",
            "    fi", '    case "${words[2]}" in']
    for name, info in data["commands"].items():
        specs = []
        for idx, choices in enumerate(info["positional"], 1):
            specs.append("'%d:value:(%s)'" % (idx, " ".join(choices)))
        for opt in info["options"]:
            flag = opt["flags"][-1]
            desc = _clean(opt["help"])
            if opt["choices"]:
                specs.append("'%s[%s]:value:(%s)'" % (flag, desc, " ".join(opt["choices"])))
            elif opt["takes_value"]:
                specs.append("'%s[%s]:value:_files'" % (flag, desc))
            else:
                specs.append("'%s[%s]'" % (flag, desc))
        if specs:
            out.append("        %s) _arguments %s ;;" % (name, " ".join(specs)))
    out += ["    esac", "}", "compdef _dpa dpa", ""]
    return "\n".join(out)


def fish(parser) -> str:
    data = collect(parser)
    out = ["# dpa fish completion (generated)", "complete -c dpa -f"]
    for name, info in data["commands"].items():
        out.append("complete -c dpa -n '__fish_use_subcommand' -a %s -d '%s'"
                   % (name, _clean(info["help"])))
    for name, info in data["commands"].items():
        for opt in info["options"]:
            line = "complete -c dpa -n '__fish_seen_subcommand_from %s'" % name
            for flag in opt["flags"]:
                line += (" -l %s" % flag[2:]) if flag.startswith("--") else (" -s %s" % flag[1:])
            if opt["choices"]:
                line += " -x -a '%s'" % " ".join(opt["choices"])
            elif opt["takes_value"]:
                line += " -r"
            line += " -d '%s'" % _clean(opt["help"])
            out.append(line)
        for choices in info["positional"]:
            out.append("complete -c dpa -n '__fish_seen_subcommand_from %s' -a '%s'"
                       % (name, " ".join(choices)))
    out.append("")
    return "\n".join(out)


GENERATORS = {"bash": bash, "zsh": zsh, "fish": fish}

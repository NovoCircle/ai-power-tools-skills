# Install and first call: the language plugin

The language plugin (`ai-power-tools-languages`) holds one guide per modeling language and the shared layout standard. It carries no program and no server. The marketplace entry of the tool plugin (`ai-power-tools`) declares it as a dependency, so installing the tool plugin brings it. Run these on a machine that has never had either plugin, against the released marketplace. Results go in the release record.

## TC-01 Installing the tool plugin brings the language plugin

Run `claude plugin marketplace add NovoCircle/ai-power-tools-skills`, then `claude plugin install ai-power-tools@novocircle`.

Passes when the install reports one dependency, `ai-power-tools-languages`, and `claude plugin list` shows both enabled at the same scope and the same version.

## TC-02 A language skill loads and answers

In a new session with no Enterprise Architect running, ask how the Business Motivation Model relates a Goal to an Objective.

Passes when `ai-power-tools-languages:bmm-1` loads and the answer cites the standard. No server call is made.

## TC-03 The layout standard is reachable from a language skill

In that session, ask what size a decision diamond is drawn at.

Passes when the answer comes from `../_languages/layout-standard.yaml`, read from the language skill's folder.

## TC-04 Removing the language plugin says what to do

Run `claude plugin disable ai-power-tools-languages`. Then run `claude plugin uninstall ai-power-tools-languages` and `claude plugin list`.

Passes when the disable is refused because the tool plugin requires it, and after the uninstall the tool plugin shows as failed to load, with a message naming the install command. Reinstall to restore it.

## TC-05 A customer on an older release updates

Starting from the release before the dependency, run `claude plugin marketplace update novocircle` and `claude plugin update ai-power-tools@novocircle`, then `claude plugin install ai-power-tools@novocircle`.

Passes when the update alone leaves the tool plugin failed to load (measured on 2026-11-04 with throwaway plugins) and the install brings the language plugin and enables both. If the update starts bringing the dependency, this case and the install section of `README.md` change together.

## TC-06 The packaged upload

Upload `dist/ai-power-tools-languages.plugin`, built by `tools/build-plugin.py`, in Claude Desktop chat or Claude Cowork. Then upload `dist/ai-power-tools.plugin`.

Passes when each loads. The archives carry no dependency declaration, so neither depends on the other being uploaded first.

## TC-07 A missing language plugin on a surface that has only the tool plugin

Where only the tool plugin is present, ask for work in a language from the table in `ea-start-here`.

Passes when the session says the guides are in a separate package, says how to install it, stops the language work, and still offers other Enterprise Architect work.

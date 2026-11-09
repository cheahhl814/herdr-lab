herdr-app: the Herdr desktop app. With no arguments it opens the window.

Usage:
  herdr-app                        open the window
  herdr-app ls                     spaces, their tabs and terminals, in the open window
  herdr-app do <command> [args]    run a command: --name api --argv '["pi"]', or one JSON object
  herdr-app feedback <text>        draft feedback for the person to review and send
  herdr-app commands               every command, its arguments, what it does
  herdr-app status                 what the window shows, and any errors
  herdr-app shot [file.png]        save the last window frame (default: herdr-shot.png)
  herdr-app check <mod folder>     load a mod once and report what's wrong
  herdr-app --skill                Agent Skill: driving the window, and where hc fits
  herdr-app --version

The terminals run in herdr-core (`hc`), which keeps them alive when the
window closes. `hc --help`: start, read, wait on and talk to terminals and
agents. The app shows them and arranges them in spaces and tabs.

Home: ~/.config/herdr-app (HERDR_APP_HOME picks another).

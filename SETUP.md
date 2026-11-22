# Setup

The OS blocks assume a fresh machine: they delete the template `~/.zshrc` that the oh-my-zsh installer writes, so that `bootstrap.sh` can link the tracked one. Run the block for your OS, then the post-install block, then the manual steps. Each block is plain bash. Machine-specific shell lines (gcloud, docker, go, op) go in `~/.zshrc.local`, which `~/.zshrc` sources when it exists.

## Ubuntu 24.04 (x86_64)

Run as a normal user with sudo. The block installs the tools with apt, GitHub release binaries and vendor install scripts, then clones this repo and runs `bootstrap.sh`. Ubuntu apt ships nvim 0.9.5, so nvim comes from the GitHub release.

```bash
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
mkdir -p ~/.local/bin

sudo apt-get update
sudo apt-get install -y git gh curl unzip zsh tmux build-essential make ripgrep fd-find jq direnv \
  ca-certificates xz-utils gzip libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev \
  libncurses-dev libffi-dev liblzma-dev tk-dev
ln -sf "$(command -v fdfind)" ~/.local/bin/fd

curl -fsSL https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz -o /tmp/nvim.tar.gz
sudo rm -rf /opt/nvim-linux-x86_64
sudo tar -C /opt -xzf /tmp/nvim.tar.gz
sudo ln -sf /opt/nvim-linux-x86_64/bin/nvim /usr/local/bin/nvim

curl -fsSL https://github.com/tree-sitter/tree-sitter/releases/latest/download/tree-sitter-linux-x64.gz | gunzip > ~/.local/bin/tree-sitter
chmod +x ~/.local/bin/tree-sitter

fingers_tag=$(curl -fsSLI -o /dev/null -w '%{url_effective}' https://github.com/Morantron/tmux-fingers/releases/latest | sed 's|.*/||')
curl -fsSL "https://github.com/Morantron/tmux-fingers/releases/download/${fingers_tag}/tmux-fingers-${fingers_tag}-linux-x86_64" -o ~/.local/bin/tmux-fingers
chmod +x ~/.local/bin/tmux-fingers

RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
[ -d ~/powerlevel10k ] || git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/powerlevel10k
[ -d ~/.tmux/plugins/tpm ] || git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | PROFILE=/dev/null bash
curl -fsSL https://pyenv.run | bash
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -fsSL https://claude.ai/install.sh | bash

[ -e ~/.config/.git ] || git clone https://github.com/nibudd/.config.git ~/.config
[ -L ~/.zshrc ] || rm -f ~/.zshrc
~/.config/bootstrap.sh

sudo chsh -s "$(command -v zsh)" "$USER"

export PATH="$HOME/.local/bin:$PATH"
~/.tmux/plugins/tpm/bin/install_plugins

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
python_version=$(pyenv install --list | grep -E '^\s*3\.[0-9]+\.[0-9]+$' | tail -1 | tr -d ' ')
pyenv install -s "$python_version"
pyenv global "$python_version"

export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install --lts
```

## macOS

Run as the logged-in user. The block installs Homebrew, then the tools, then clones this repo and runs `bootstrap.sh`.

```bash
set -eo pipefail

command -v brew >/dev/null || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/opt/homebrew/bin/brew shellenv)"

brew install git gh curl unzip zsh tmux neovim tree-sitter-cli make ripgrep fd jq direnv uv pyenv \
  openssl readline sqlite3 xz zlib tcl-tk powerlevel10k tmux-fingers cormacrelf/tap/dark-notify

RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
[ -d ~/.tmux/plugins/tpm ] || git clone https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm

curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/master/install.sh | PROFILE=/dev/null bash
curl -fsSL https://claude.ai/install.sh | bash

[ -e ~/.config/.git ] || git clone https://github.com/nibudd/.config.git ~/.config
[ -L ~/.zshrc ] || rm -f ~/.zshrc
~/.config/bootstrap.sh

export PATH="$HOME/.local/bin:$PATH"
~/.tmux/plugins/tpm/bin/install_plugins

eval "$(pyenv init - bash)"
python_version=$(pyenv install --list | grep -E '^\s*3\.[0-9]+\.[0-9]+$' | tail -1 | tr -d ' ')
pyenv install -s "$python_version"
pyenv global "$python_version"

export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install --lts
```

## Post-install (both OSes)

Run after the OS block, in a zsh shell that loads `~/.zshrc`, so that node and npm from nvm are on PATH. It syncs the nvim plugins, installs the Mason tools (the `ensure_installed` servers in `nvim/lua/plugins/lsp/lsp.lua`, `stylua` and `eslint_d`), and installs the treesitter parsers listed in `nvim/lua/plugins/syntax/treesitter.lua`.

```bash
zsh -i -c '
set -e
nvim --headless "+Lazy! sync" +qa
nvim --headless \
  "+MasonInstall lua-language-server basedpyright typescript-language-server vue-language-server stylua eslint_d" \
  "+lua local r = require(\"mason-registry\"); local names = {\"lua-language-server\", \"basedpyright\", \"typescript-language-server\", \"vue-language-server\", \"stylua\", \"eslint_d\"}; assert(vim.wait(900000, function() for _, n in ipairs(names) do if not r.is_installed(n) then return false end end return true end, 1000), \"mason install timed out\")" \
  +qa
nvim --headless \
  "+lua assert(require(\"nvim-treesitter\").install({\"bash\", \"css\", \"html\", \"javascript\", \"lua\", \"python\", \"sql\", \"typescript\", \"vim\", \"vimdoc\", \"vue\"}):wait(900000))" \
  +qa
'
```

## Manual steps

These need a person or a browser, so no block runs them.

1. Set the git identity: `git config --global user.name "<name>"` and `git config --global user.email "<email>"`.
2. Create a GitHub SSH key with `ssh-keygen -t ed25519`, add the public key at github.com/settings/keys, then run `gh auth login`.
3. Switch the repo remote to SSH: `git -C ~/.config remote set-url origin git@github.com:nibudd/.config.git`. Re-run `~/.config/bootstrap.sh` so it can clone `~/.claude-work`.
4. macOS only: turn on brew autoupdate with `brew tap domt4/autoupdate && brew autoupdate start`.
5. macOS only: turn off natural scrolling for the mouse in System Settings, Mouse, Natural scrolling.
6. Put machine-specific lines (gcloud, docker, go, op) in `~/.zshrc.local`.

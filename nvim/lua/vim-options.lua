vim.cmd("set autoindent")
vim.cmd("set autowrite")
vim.cmd("set autowriteall")
vim.cmd("set colorcolumn=89")
vim.cmd("set cursorline")
vim.cmd("set cursorcolumn")
vim.cmd("set expandtab")
vim.cmd("set ignorecase")
vim.cmd("set nowrap")
vim.cmd("set relativenumber")
vim.cmd("set autoread")
vim.cmd("set shiftwidth=4")
vim.cmd("set smartcase")
vim.cmd("set smartindent")
vim.cmd("set splitright")
vim.cmd("set softtabstop=4")
vim.cmd("set tabstop=4")
vim.g.mapleader = " "

-- Navigate vim panes better
vim.keymap.set('n', '<c-k>', ':wincmd k<CR>')
vim.keymap.set('n', '<c-j>', ':wincmd j<CR>')
vim.keymap.set('n', '<c-h>', ':wincmd h<CR>')
vim.keymap.set('n', '<c-l>', ':wincmd l<CR>')

vim.keymap.set('n', '<leader>h', ':nohlsearch<CR>')
vim.wo.number = true


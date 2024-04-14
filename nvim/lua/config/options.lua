-- backup
vim.opt.backup = false
vim.opt.swapfile = false
vim.opt.undodir = os.getenv("HOME") .. "/.vim/undodir"
vim.opt.undofile = true

-- colours
vim.opt.colorcolumn = "80"
vim.opt.termguicolors = true

-- cursor
vim.opt.guicursor = ""

-- gutter
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.signcolumn = "yes"

-- lines
vim.opt.expandtab = true
vim.opt.scrolloff = 5
vim.opt.shiftwidth = 4
vim.opt.softtabstop = 4
vim.opt.smartindent = true
vim.opt.tabstop = 4
vim.opt.wrap = false

-- miscellaneous
vim.opt.isfname:append("@-@")
vim.opt.updatetime = 50

-- new split positions
vim.opt.splitbelow = true
vim.opt.splitright = true

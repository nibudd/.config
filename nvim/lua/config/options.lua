-- backup
vim.opt.backup = false
vim.opt.swapfile = false
vim.opt.undodir = os.getenv("HOME") .. "/.vim/undodir"
vim.opt.undofile = true

-- colours
vim.opt.colorcolumn = "88"
vim.opt.termguicolors = true

-- cursor
vim.opt.guicursor = ""
vim.opt.cursorline = true
vim.opt.cursorcolumn = true

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
vim.opt.updatetime = 50

-- search
vim.opt.ignorecase = true
vim.opt.smartcase = true

-- new split positions
vim.opt.splitbelow = true
vim.opt.splitright = true

-- folding
vim.wo.foldlevel = 99
vim.wo.foldenable = true
vim.wo.foldmethod = "expr"
vim.wo.foldexpr = "nvim_treesitter#foldexpr()"

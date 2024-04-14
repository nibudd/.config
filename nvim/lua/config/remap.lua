vim.g.mapleader = " "

-- move selections
vim.keymap.set("x", "J", ":m '>+1<CR>gv=gv")
vim.keymap.set("x", "K", ":m '<-2<CR>gv=gv")

-- join lines without moving the cursor
vim.keymap.set("n", "J", "mzJ`z")

-- centre cursor for half-page jumps
vim.keymap.set("n", "<C-d>", "<C-d>zz")
vim.keymap.set("n", "<C-u>", "<C-u>zz")

-- keep searches centered and unfolded
vim.keymap.set("n", "n", "nzzzv")
vim.keymap.set("n", "N", "Nzzzv")

-- easier yanking to the clipboard register
vim.keymap.set({"n", "x"}, "<leader>y", "\"*y")
vim.keymap.set("n", "<leader>Y", "\"*Y")

-- easier no-yank deleting
vim.keymap.set({"n", "x"}, "<leader>d", "\"*d")

-- substitute under cursor
vim.keymap.set("n", "<leader>s", [[:%s/\<<C-r><C-w>\>//gI<Left><Left><Left>]])

-- make current file executable
vim.keymap.set("n", "<leader>x", "<cmd>!chmod +x %<CR>", { silent = true })

-- easier access to :nohlsearch
vim.keymap.set("n", "<leader>hl", ":nohlsearch<CR>")

-- easier window navigation
vim.keymap.set("n", "<C-S-H>", "<C-w><C-h>")
vim.keymap.set("n", "<C-S-J>", "<C-w><C-j>")
vim.keymap.set("n", "<C-S-K>", "<C-w><C-k>")
vim.keymap.set("n", "<C-S-l>", "<C-w><C-l>")

-- open help vertically
vim.keymap.set("n", ":H", ":vert help ")

-- charwise-visual of the whole line
vim.keymap.set("n", "vv", "_v$")

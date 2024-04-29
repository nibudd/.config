vim.g.mapleader = " "

vim.keymap.set("x", "J", ":m '>+1<CR>gv=gv", {desc="move selected lines down"})
vim.keymap.set("x", "K", ":m '<-2<CR>gv=gv", {desc="move selected lines up"})

vim.keymap.set("n", "J", "mzJ`z", {desc="join lines without moving cursor"})

vim.keymap.set("n", "<C-d>", "<C-d>zz", {desc="centre cursor for half-page jumps down"})
vim.keymap.set("n", "<C-u>", "<C-u>zz", {desc="centre cursor for half-page jumps up"})

vim.keymap.set("n", "n", "nzzzv", {desc="keep search selections centered and unfolded"})
vim.keymap.set("n", "N", "Nzzzv", {desc="keep search selections centered and unfolded"})

vim.keymap.set({"n", "x"}, "<leader>y", "\"*y", {desc="yank to the clipboard register"})
vim.keymap.set("n", "<leader>Y", "\"*Y", {desc="yank line to the clipboard register"})

vim.keymap.set({"n", "x"}, "<leader>d", "\"_d", {desc="no-yank deleting"})

vim.keymap.set("n", "<leader>s", [[:%s/\<<C-r><C-w>\>//gI<Left><Left><Left>]], {desc="open file-range substitute for word under cursor"})

vim.keymap.set("n", "<leader>nh", "<cmd>nohlsearch<CR>", {desc="set nohlsearch"})

vim.keymap.set("n", "vv", "_v$", {desc="charwise-visual selection of current line without leading whitespace"})

vim.keymap.set("n", "<leader>map",
    function()
        vim.cmd("redir! > user-remaps.txt")
        vim.cmd("silent map")
        vim.cmd("redir END")
        vim.cmd("edit user-remaps.txt")
    end,
    {desc="open user-defined mappings in a buffer"}
)

vim.g.mapleader = " "

vim.keymap.set("n", "<C-h>", "<C-w>h", { desc = "move left one pane" })
vim.keymap.set("n", "<C-j>", "<C-w>j", { desc = "move down one pane" })
vim.keymap.set("n", "<C-k>", "<C-w>k", { desc = "move up one pane" })
vim.keymap.set("n", "<C-l>", "<C-w>l", { desc = "move right one pane" })

vim.keymap.set("i", "jk", "<esc><cmd>update<CR>", { desc = "exit insert mode and update" })
vim.keymap.set("i", "jq", "<esc><cmd>update<CR><cmd>q<CR>", { desc = "exit insert mode, update, and quit" })
vim.keymap.set("n", "<leader>jk", "<cmd>update<CR>", { desc = "update from normal mode" })
vim.keymap.set("n", "<leader>jq", "<cmd>update<CR><cmd>q<CR>", { desc = "update from normal mode and quit" })

vim.keymap.set("x", "J", ":m '>+1<CR>gv=gv", { desc = "move selected lines down" })
vim.keymap.set("x", "K", ":m '<-2<CR>gv=gv", { desc = "move selected lines up" })

vim.keymap.set("n", "<leader>J", "mzJx`z", {desc="join lines without any whitespace or moving cursor"})
vim.keymap.set("n", "J", "mzJ`z", {desc="join lines without moving cursor"})

vim.keymap.set("n", "<C-d>", "<C-d>zz", { desc = "centre cursor for half-page jumps down" })
vim.keymap.set("n", "<C-u>", "<C-u>zz", { desc = "centre cursor for half-page jumps up" })

vim.keymap.set("n", "n", "nzzzv", { desc = "keep search selections centered and unfolded" })
vim.keymap.set("n", "N", "Nzzzv", { desc = "keep search selections centered and unfolded" })

vim.keymap.set({ "n", "x" }, "<leader>y", "\"*y", { desc = "yank to the clipboard register" })
vim.keymap.set("n", "<leader>Y", "\"*Y", { desc = "yank line to the clipboard register" })

vim.keymap.set({ "n", "x" }, "<leader>c", "\"_c", { desc = "no-yank change" })
vim.keymap.set({ "n", "x" }, "<leader>C", "\"_C", { desc = "no-yank change to end of line" })
vim.keymap.set({ "n", "x" }, "<leader>d", "\"_d", { desc = "no-yank motion delete" })
vim.keymap.set({ "n", "x" }, "<leader>D", "\"_D", { desc = "no-yank delete to end of line" })
vim.keymap.set({ "n", "x" }, "<leader>x", "\"_x", { desc = "no-yank character delete" })
vim.keymap.set({ "n", "x" }, "<leader>X", "\"_X", { desc = "no-yank backwards character delete" })

vim.keymap.set("n", "<leader>s", [[:%s/\<<C-r><C-w>\>//gI<Left><Left><Left>]],
    { desc = "open file-range substitute for word under cursor" })

vim.keymap.set("n", "<leader>nh", "<cmd>nohlsearch<CR>", { desc = "set nohlsearch" })

vim.keymap.set("n", "vv", "_v$", { desc = "charwise-visual selection of current line without leading whitespace" })

vim.keymap.set("n", "<leader>map",
    function()
        vim.cmd("redir! > user-remaps.txt")
        vim.cmd("silent map")
        vim.cmd("redir END")
        vim.cmd("edit user-remaps.txt")
    end,
    { desc = "open user-defined mappings in a buffer" }
)

vim.keymap.set("n", "<leader>%",
    function()
        vim.cmd([[let @f = expand("%:p")]])
    end,
    { desc = "yank absolute filepath to register f" }
)

vim.keymap.set('n',        's', '<Plug>(leap)')
vim.keymap.set('n',        'S', '<Plug>(leap-from-window)')
vim.keymap.set({'x', 'o'}, 's', '<Plug>(leap-forward)')
vim.keymap.set({'x', 'o'}, 'S', '<Plug>(leap-backward)')

vim.keymap.set("n", "<leader>lq", "<cmd>call setloclist(0, [], ' ', {'items': get(getqflist({'items': 1}), 'items')})<CR><cmd>cclose<CR><cmd>lopen<CR>", { desc = "copy quickfix list to local list" })
vim.keymap.set("n", "<leader>ln", "<cmd>:lne<CR>", { desc = "move to the next local list item" })
vim.keymap.set("n", "<leader>lb", "<cmd>:lp<CR>", { desc = "move to the previous local list item" })


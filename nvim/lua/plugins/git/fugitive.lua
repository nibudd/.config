-- git commands and integration
return {
    "tpope/vim-fugitive",
    config = function()
		vim.keymap.set("n", "<leader>gg", ":Git ")
    end
}

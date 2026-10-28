-- fuzzy finder

local hidden_allow = vim.fn.stdpath("config") .. "/rg-hidden-allow"

return {
	"nvim-telescope/telescope.nvim",
	version = "*",
	dependencies = { "nvim-lua/plenary.nvim" },
	keys = {
		{
			"<leader>ff",
			function()
				require("telescope.builtin").find_files({
					find_command = { "rg", "--files", "--color", "never", "--ignore-file", hidden_allow },
				})
			end,
			desc = "find files, respecting .gitignore but including allowed hidden files",
		},
		{
			"<leader>ls",
			function()
				require("telescope.builtin").buffers({ sort_mru = true })
			end,
			desc = "list active buffers ordered by most recently used",
		},
		{
			"<leader>lg",
			function()
				require("telescope.builtin").live_grep({ additional_args = { "--ignore-file", hidden_allow } })
			end,
			desc = "live grep, respecting .gitignore but including allowed hidden files",
		},
		{
			"<leader>wg",
			function()
				require("telescope.builtin").live_grep({
					additional_args = { "--ignore-file", hidden_allow },
					default_text = vim.fn.expand("<cword>"),
				})
			end,
			desc = "open live grep with the word under the cursor",
		},
	},
	config = function()
		require("telescope").load_extension("fzf")
	end,
}

-- auto-select theme based on system theme
return {
	{
		"cormacrelf/dark-notify",
		cond = vim.fn.executable("dark-notify") == 1,
		config = function()
			require("dark_notify").run({
				schemes = {
					light = { colorscheme = "catppuccin-latte" },
					dark = { colorscheme = "catppuccin-frappe" },
				},
			})
		end,
	},
}

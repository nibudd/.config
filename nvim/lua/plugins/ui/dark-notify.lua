-- auto-select theme based on system theme
return {
	{
		"cormacrelf/dark-notify",
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

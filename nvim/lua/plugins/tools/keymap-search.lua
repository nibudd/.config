-- searchable telescope window for keybindings with descriptions
return {
    "nvim-telescope/telescope.nvim",
    keys = {
        {
            "<leader>map",
            function()
                require("telescope.builtin").keymaps({
                    show_plug = false,
                    layout_config = {
                        width = 0.9,
                        height = 0.8,
                        preview_width = 0.4,
                    },
                })
            end,
            desc = "Search keymaps with Telescope",
        },
    },
}

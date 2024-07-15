-- file tree navigator
return {
    "nvim-neo-tree/neo-tree.nvim",
    branch = "v3.x",
    dependencies = {
      "nvim-lua/plenary.nvim",
      "nvim-tree/nvim-web-devicons", -- not strictly required, but recommended
      "MunifTanjim/nui.nvim",
      "3rd/image.nvim", -- Optional image support in preview window: See `# Preview Mode` for more information
    },
    config = function ()
        require("neo-tree").setup({
            window = {
                mappings = {
                    ["P"] = { "toggle_preview", config = { use_float = true, use_image_nvim = false } },
                    ['e'] = function() vim.api.nvim_exec('Neotree filesystem reveal', true) end,
                    ['b'] = function() vim.api.nvim_exec('Neotree buffers', true) end,
                    ['h'] = function() vim.api.nvim_exec('Neotree git_status', true) end,
                },
                position = "float",
            },
            filesystem = {
                components = {
                    harpoon_index = function(config, node, _)
                        local harpoon_list = require("harpoon"):list()
                        local path = node:get_id()
                        local harpoon_key = vim.uv.cwd()

                        for i, item in ipairs(harpoon_list.items) do
                            local value = item.value
                            if string.sub(item.value, 1, 1) ~= "/" then
                                value = harpoon_key .. "/" .. item.value
                            end

                            if value == path then
                                vim.print(path)
                                return {
                                    text = string.format(" ⥤ %d", i), -- <-- Add your favorite harpoon like arrow here
                                    highlight = config.highlight or "NeoTreeDirectoryIcon",
                                }
                            end
                        end
                        return {}
                    end,
                },
                renderers = {
                    file = {
                        { "icon" },
                        { "name", use_git_status_colors = true },
                        { "harpoon_index" }, --> This is what actually adds the component in where you want it
                        { "diagnostics" },
                        { "git_status", highlight = "NeoTreeDimText" },
                    },
                },
                hijack_netrw_behavior = "open_current",
            },
            default_component_configs = {
                diagnostics = {
                    symbols = {
                        hint = " ",
                        info = " ",
                        warn = " ",
                        error = "󰌵 ",
                    },
                    highlights = {
                        hint = "DiagnosticSignHint",
                        info = "DiagnosticSignInfo",
                        warn = "DiagnosticSignWarn",
                        error = "DiagnosticSignError",
                    },
                },
            }
        })
        vim.keymap.set("n", "<leader>ex", "<cmd>Neotree reveal<CR>")
    end
}



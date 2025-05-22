-- status bar
return {
    'nvim-lualine/lualine.nvim',
    dependencies = { 'nvim-tree/nvim-web-devicons' },
    config = function()
        require('lualine').setup {
            options = {
                icons_enabled = true,
                theme = 'auto',
                component_separators = { left = '', right = '' },
                section_separators = { left = '', right = '' },
                disabled_filetypes = {
                    statusline = {},
                    winbar = {},
                },
                ignore_focus = {},
                always_divide_middle = true,
                globalstatus = false,
                refresh = {
                    statusline = 1000,
                    tabline = 1000,
                    winbar = 1000,
                },
            },
            sections = {
                lualine_a = {
                    {
                        "mode",
                    },
                },
                lualine_b = {
                    {
                        "filetype",
                        colored = true, -- Displays filetype icon in color if set to true
                        icon_only = true, -- Display only an icon for filetype
                        icon = { align = 'right' }, -- Display filetype icon on the right hand side
                        separator = "",
                    },
                    {
                        "filename",
                        newfile_status = true,
                        padding = { right = 2 },
                        path = 3,
                        symbols = {
                            modified = '✏️', -- Text to show when the file is modified.
                            readonly = '🔎', -- Text to show when the file is non-modifiable or readonly.
                            unnamed = '🫥', -- Text to show for unnamed buffers.
                            newfile = '⭐️', -- Text to show for newly created file before first write
                        },
                        fmt = function(val)
                            return vim.api.nvim_get_current_buf().. " " .. val
                        end
                    },
                },
                lualine_c = {
                    {
                        "harpoon2",
                        icon = '🪝',
                        indicators = { "1", "2", "3", "4" },
                        active_indicators = { "1️⃣", "2️⃣", "3️⃣", "4️⃣" },
                        _separator = "  ",
                        no_harpoon = "Harpoon not loaded",
                    },
                },
                lualine_x = {},
                lualine_y = {},
                lualine_z = {}
            },
            inactive_sections = {
                lualine_a = { 'mode' },
                lualine_b = {
                    {
                        "filetype",
                        colored = true, -- Displays filetype icon in color if set to true
                        icon_only = true, -- Display only an icon for filetype
                        icon = { align = 'right' }, -- Display filetype icon on the right hand side
                        separator = "",
                    },
                    {
                        "filename",
                        newfile_status = true,
                        padding = { right = 2 },
                        path = 3,
                        symbols = {
                            modified = '✏️', -- Text to show when the file is modified.
                            readonly = '🔎', -- Text to show when the file is non-modifiable or readonly.
                            unnamed = '🫥', -- Text to show for unnamed buffers.
                            newfile = '⭐️', -- Text to show for newly created file before first write
                        }
                    },
                },
                lualine_c = {
                    {
                        "harpoon2",
                        icon = '🪝',
                        indicators = { "1", "2", "3", "4" },
                        active_indicators = { "1️⃣", "2️⃣", "3️⃣", "4️⃣" },
                        _separator = "  ",
                        no_harpoon = "Harpoon not loaded",
                    },
                },
                lualine_x = {},
                lualine_y = {},
                lualine_z = {}
            },
            tabline = {
                lualine_a = {
                    {
                        "branch",
                        separator = "",
                    },
                },
                lualine_b = {
                    'diff',
                },
                lualine_c = {
                    {
                        'diagnostics',

                        -- Table of diagnostic sources, available sources are:
                        --   'nvim_lsp', 'nvim_diagnostic', 'nvim_workspace_diagnostic', 'coc', 'ale', 'vim_lsp'.
                        -- or a function that returns a table as such:
                        --   { error=error_cnt, warn=warn_cnt, info=info_cnt, hint=hint_cnt }
                        sources = { 'nvim_diagnostic', 'coc' },

                        -- Displays diagnostics for the defined severity types
                        sections = { 'error', 'warn', 'info', 'hint' },

                        diagnostics_color = {
                            -- Same values as the general color option can be used here.
                            error = 'DiagnosticError', -- Changes diagnostics' error color.
                            warn  = 'DiagnosticWarn',  -- Changes diagnostics' warn color.
                            info  = 'DiagnosticInfo',  -- Changes diagnostics' info color.
                            hint  = 'DiagnosticHint',  -- Changes diagnostics' hint color.
                        },
                        symbols = { error = 'E', warn = 'W', info = 'I', hint = 'H' },
                        colored = true,          -- Displays diagnostics status in color if set to true.
                        update_in_insert = true, -- Update diagnostics in insert mode.
                        always_visible = false,  -- Show diagnostics even if there are none.
                    },
                    {
                        "tabs",
                        tab_max_length = 20,
                        max_length = vim.o.columns,
                        mode = 2,
                        path = 0,
                    },
                },
                lualine_x = { 'encoding', 'fileformat' },
                lualine_y = { 'progress' },
                lualine_z = { 'location' }
            },
            winbar = {},
            inactive_winbar = {},
            extensions = {}
        }
    end
}

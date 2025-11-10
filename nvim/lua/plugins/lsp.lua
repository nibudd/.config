return {
    -- Mason
    {
        "williamboman/mason.nvim",
        priority = 1000, -- Load first
        config = function()
            require("mason").setup()
        end
    },

    -- Mason-lspconfig
    {
        "williamboman/mason-lspconfig.nvim",
        priority = 999,
        dependencies = { "williamboman/mason.nvim" },
        config = function()
            require("mason-lspconfig").setup({
                ensure_installed = { "lua_ls", "pyright" },
            })
        end
    },

    -- LSP Configuration
    {
        "neovim/nvim-lspconfig",
        event = { "BufReadPre", "BufNewFile" },
        priority = 998,
        dependencies = {
            "williamboman/mason.nvim",
            "williamboman/mason-lspconfig.nvim",
            "hrsh7th/cmp-nvim-lsp",
        },
        config = function()
            local border = "rounded"

            -- Configure LSP handlers with borders BEFORE any servers are set up
            local orig_util_open_floating_preview = vim.lsp.util.open_floating_preview
            function vim.lsp.util.open_floating_preview(contents, syntax, opts, ...)
                opts = opts or {}
                opts.border = border
                return orig_util_open_floating_preview(contents, syntax, opts, ...)
            end

            -- Also set the handlers (belt and suspenders approach)
            vim.lsp.handlers["textDocument/hover"] = vim.lsp.with(
                vim.lsp.handlers.hover, { 
                    border = border,
                    max_width = 80,
                    max_height = 20,
                }
            )
            vim.lsp.handlers["textDocument/signatureHelp"] = vim.lsp.with(
                vim.lsp.handlers.signature_help, { 
                    border = border,
                    max_width = 80,
                    max_height = 20,
                }
            )
            
            -- Configure diagnostics with borders
            vim.diagnostic.config({
                float = { 
                    border = border,
                    source = "always",
                    header = "",
                    prefix = "",
                },
            })

            local capabilities = require('cmp_nvim_lsp').default_capabilities()
            -- local lspconfig = require("lspconfig")
            
            -- Setup lua_ls
            vim.lsp.config['lua_ls'] = {
                capabilities = capabilities,
                settings = {
                    Lua = {
                        diagnostics = { globals = { "vim" } },
                        workspace = { 
                            library = vim.api.nvim_get_runtime_file("", true),
                            checkThirdParty = false,
                        },
                        telemetry = { enable = false },
                    },
                },
            }

            -- Setup pyright
            vim.lsp.config['pyright'] = {
                capabilities = capabilities,
            }

            -- Add keymaps and test border functionality
            vim.api.nvim_create_autocmd("LspAttach", {
                group = vim.api.nvim_create_augroup("UserLspConfig", {}),
                callback = function(ev)
                    local opts = { buffer = ev.buf }
                    
                    -- Custom hover function to ensure borders
                    vim.keymap.set("n", "K", function()
                        vim.lsp.buf.hover()
                    end, opts)
                    
                    vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
                    vim.keymap.set("n", "gr", vim.lsp.buf.references, opts)
                    vim.keymap.set("n", "ge", vim.diagnostic.open_float, opts)
                    
                    -- Debug function to test borders
                    vim.keymap.set("n", "<leader>test", function()
                        vim.lsp.util.open_floating_preview(
                            {"Test border", "This should have a border"},
                            "markdown",
                            { border = border }
                        )
                    end, opts)
                end,
            })
        end,
    },

    -- nvim-cmp
    {
        'hrsh7th/nvim-cmp',
        event = 'InsertEnter',
        dependencies = {
            'hrsh7th/cmp-nvim-lsp',
            'hrsh7th/cmp-buffer',
            'hrsh7th/cmp-path',
            'hrsh7th/cmp-cmdline',
            'hrsh7th/cmp-vsnip',
            'hrsh7th/vim-vsnip',
        },
        config = function()
            local cmp = require('cmp')

            cmp.setup({
                snippet = {
                    expand = function(args)
                        vim.fn["vsnip#anonymous"](args.body)
                    end,
                },
                window = {
                    completion = cmp.config.window.bordered(),
                    documentation = cmp.config.window.bordered(),
                },
                mapping = cmp.mapping.preset.insert({
                    ['<C-b>'] = cmp.mapping.scroll_docs(-4),
                    ['<C-f>'] = cmp.mapping.scroll_docs(4),
                    ['<C-Space>'] = cmp.mapping.complete(),
                    ['<C-e>'] = cmp.mapping.abort(),
                    ['<CR>'] = cmp.mapping.confirm({ select = false }),
                }),
                sources = cmp.config.sources({
                    { name = 'nvim_lsp' },
                    { name = 'vsnip' },
                }, {
                    { name = 'buffer' },
                })
            })

            cmp.setup.cmdline({ '/', '?' }, {
                mapping = cmp.mapping.preset.cmdline(),
                sources = { { name = 'buffer' } }
            })

            cmp.setup.cmdline(':', {
                mapping = cmp.mapping.preset.cmdline(),
                sources = cmp.config.sources({
                    { name = 'path' }
                }, {
                    { name = 'cmdline' }
                }),
                matching = { disallow_symbol_nonprefix_matching = false }
            })
        end,
    },
}

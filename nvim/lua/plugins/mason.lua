-- a modified lsp-zero configuration of nvim's LSP
return {
    {
        "mason-org/mason.nvim",
        opts = {}
    },
    {
        "mason-org/mason-lspconfig.nvim",
        opts = {},
        dependencies = {
            { "mason-org/mason.nvim", opts = {} },
            "neovim/nvim-lspconfig",
        },
    },
    -- non lsp-zero alternatives that i haven't got working the way i want yet
    -- { "echasnovski/mini.completion", version = '*' },
    -- { "echasnovski/mini.snippets", version = '*' },
    -- { "echasnovski/mini.icons", version = '*' },
    -- {
    --     "hrsh7th/nvim-cmp",
    --     -- version = false, -- last release is way too old
    --     -- event = "InsertEnter",
    --     -- dependencies = {
    --     --   "hrsh7th/cmp-nvim-lsp",
    --     --   "hrsh7th/cmp-buffer",
    --     --   "hrsh7th/cmp-path",
    --     -- },
    --     -- Not all LSP servers add brackets when completing a function.
    --     -- To better deal with this, LazyVim adds a custom option to cmp,
    --     -- that you can configure. For example:
    --     --
    --     -- ```lua
    --     -- opts = {
    --     --   auto_brackets = { "python" }
    --     -- }
    --     -- ```
    --     opts = function()
    --         local cmp = require("cmp")
    --         return {
    --             window = {
    --                 completion = cmp.config.window.bordered(),
    --                 documentation = cmp.config.window.bordered(),
    --             },
    --             -- mapping = cmp.mapping.preset.insert({
    --             --     -- Enter key confirms completion item
    --             --     ["<CR>"] = cmp.confirm({ select = false }),
    --             --
    --             --     -- Ctrl + space triggers completion menu
    --             --     ["<C-Space>"] = cmp.mapping.complete(),
    --             --
    --             -- }),
    --             -- snippet = {
    --             --     expand = function(args)
    --             --         require('luasnip').lsp_expand(args.body)
    --             --     end,
    --             -- },
    --         }
    --     end,
    --     -- main = "lazyvim.util.cmp",
    -- },

    -- lsp zero config which seems to still work for now
    {
        'VonHeikemen/lsp-zero.nvim',
        branch = 'v3.x',
        config = function()
            local lsp_zero = require('lsp-zero')
            lsp_zero.extend_lspconfig()

            ---@diagnostic disable-next-line: unused-local
            lsp_zero.on_attach(function(client, bufnr)
                -- see :help lsp-zero-keybindings
                -- to learn the available actions
                lsp_zero.default_keymaps({ buffer = bufnr })
            end)

            require("mason").setup({})
            require("mason-lspconfig").setup({
                handlers = {
                    lsp_zero.default_setup,
                    lua_ls = function()
                        local lua_opts = lsp_zero.nvim_lua_ls()
                        require("lspconfig").lua_ls.setup(lua_opts)
                    end,
                },
            })

            local cmp = require('cmp')
            ---@diagnostic disable-next-line: unused-local
            local cmp_action = require('lsp-zero').cmp_action()

            cmp.setup({
                window = {
                    completion = cmp.config.window.bordered(),
                    documentation = cmp.config.window.bordered(),
                },
                -- see :help lsp-zero-completion-keybindings
                -- to learn the available actions
                mapping = cmp.mapping.preset.insert({
                    -- Enter key confirms completion item
                    ['<CR>'] = cmp.mapping.confirm({ select = false }),

                    -- Ctrl + space triggers completion menu
                    ['<C-Space>'] = cmp.mapping.complete(),

                    -- ['<C-Space>'] = cmp.mapping.complete(),
                    -- ['<C-f>'] = cmp_action.luasnip_jump_forward(),
                    -- ['<C-b>'] = cmp_action.luasnip_jump_backward(),
                    -- ['<C-u>'] = cmp.mapping.scroll_docs(-4),
                    -- ['<C-d>'] = cmp.mapping.scroll_docs(4),
                }),
                snippet = {
                    expand = function(args)
                        require('luasnip').lsp_expand(args.body)
                    end,
                },
            })
        end
    },
    { 'hrsh7th/nvim-cmp' },
    { 'neovim/nvim-lspconfig' },
    { 'hrsh7th/cmp-nvim-lsp' },
    { 'L3MON4D3/LuaSnip' },
}

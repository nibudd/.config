return {
	{
		"williamboman/mason-lspconfig.nvim",
		lazy = false,
		opts = {
			auto_install = true,
		},
		config = function()
			local mason_lspconfig = require("mason-lspconfig")
			mason_lspconfig.setup({
				ensure_installed = {
					"pylsp",
				},
				auto_install = true,
			})
		end,
	},
	{
		"neovim/nvim-lspconfig",
		lazy = false,
		config = function()
			local capabilities = require("cmp_nvim_lsp").default_capabilities()
			local lspconfig = require("lspconfig")
			lspconfig.pylsp.setup({
				capabilities = capabilities,
				python = {
					analysis = {
						autoSearchPaths = true,
						useLibraryCodeForTypes = true,
						autoImportCompletions = true,
					},
                    -- pythonpath = vim.fn.getcwd() .. "/venv/bin/python",
                    -- pythonpath = "/Users/nathanbudd/dev/audette/micro-services/venv/bin/python",
                    pythonpath = vim.fn.getcwd() .. "/venv/bin/python3"
				},
                -- settings = {
                --     pylsp = {
                --         plugins = {
                --             rope_autoimport = {
                --                 enabled = true
                --             }
                --         }
                --     }
                -- }
			})

            vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
            vim.keymap.set("n", "gD", vim.lsp.buf.hover, opts)
            vim.keymap.set('n', '<leader>d', vim.diagnostic.open_float)
            vim.keymap.set("n", "<leader>n", vim.diagnostic.goto_next, opts)
            vim.keymap.set("n", "<leader>p", vim.diagnostic.goto_prev, opts)
            vim.keymap.set("n", "<leader>ca", vim.lsp.buf.code_action, opts)
            vim.keymap.set('n', 'gr', function()
                require('telescope.builtin').lsp_references({ jump_type = "never" })
            end, {silent = true})
            vim.keymap.set("n", "<leader>rn", vim.lsp.buf.rename, opts)
            vim.keymap.set("i", "<leader>h", vim.lsp.buf.signature_help, opts)
            vim.keymap.set("n", 'gh', '<cmd>ClangdSwitchSourceHeader<cr>')

			vim.api.nvim_create_autocmd("LspAttach", {
				group = vim.api.nvim_create_augroup("UserLspConfig", {}),
				callback = function(ev)
					local opts = { buffer = ev.buf }
			    vim.keymap.set("n", "<leader>rn", vim.lsp.buf.rename, opts)
				end,
			})
		end,
	},
    {
        "python-rope/pylsp-rope"
    },
    -- {
    --     "paradoxxxzero/pyls-isort"
    -- },
}

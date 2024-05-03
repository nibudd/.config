return {
    "mfussenegger/nvim-dap",
    dependencies = {
        "mfussenegger/nvim-dap-python",
        "nvim-neotest/nvim-nio",
        "rcarriga/nvim-dap-ui",
        "tpope/vim-fugitive",
    },
    config = function()
        require("dapui").setup()
        require("dap-python").setup(
            "~/.local/share/nvim/mason/packages/debugpy/venv/bin/python"
            -- vim.fn.getcwd() .. '/venv/bin/python'
        )
        local dap, dapui = require("dap"), require("dapui")
        require("dap-python").test_runner = "pytest"

        dap.listeners.before.attach.dapui_config = function()
            dapui.open()
        end
        dap.listeners.before.launch.dapui_config = function()
            dapui.open()
        end
        dap.listeners.before.event_terminated.dapui_config = function()
            dapui.close()
        end
        dap.listeners.before.event_exited.dapui_config = function()
            dapui.close()
        end

        vim.keymap.set("n", "<Leader>bp", ":DapToggleBreakpoint<CR>", {desc="DAP: toggle breakpoint"})
        vim.keymap.set("n", "<Leader>dc", ":DapContinue<CR>", {desc="DAP: start/continue debugging"})
        vim.keymap.set("n", "<Leader>dx", ":DapTerminate<CR>", {desc="DAP: stop debugging"})
        vim.keymap.set("n", "<Leader>dn", ":DapStepOver<CR>", {desc="DAP: step over"})
        vim.keymap.set("n", "<Leader>ds", ":DapStepInto<CR>", {desc="DAP: step into"})
        vim.keymap.set("n", "<Leader>dr", ":DapStepOut<CR>",  {desc="DAP: step out"})
    end,
}

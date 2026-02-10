return {
    "selimacerbas/markdown-preview.nvim",
    dependencies = { "selimacerbas/live-server.nvim" },
    config = function()
        require("markdown_preview").setup({
            port = 8421,                     -- server port
            open_browser = true,             -- auto-open browser on start

            content_name = "content.md",     -- workspace content file
            index_name = "index.html",       -- workspace HTML file
            workspace_dir = nil,             -- nil = per-buffer (recommended); set a path to override

            overwrite_index_on_start = true, -- copy plugin's index.html on every start

            auto_refresh = true,             -- auto-update on buffer changes
            auto_refresh_events = {          -- which events trigger refresh
                "InsertLeave", "TextChanged", "TextChangedI", "BufWritePost"
            },
            debounce_ms = 300,         -- debounce interval
            notify_on_refresh = false, -- show notification on refresh
        })
    end,
}

local path = vim.api.nvim_buf_get_name(0)
local mdkite = require("mdkite")

mdkite.setup({ instance_mode = "multi", port = 0, open_browser = vim.env.PREVIEW_NO_BROWSER == nil })

local function reload()
	vim.cmd("checktime")
	mdkite.refresh()
end

-- Watches the directory, because editors replace the file on write and a file watch dies with the old inode.
local watcher = vim.uv.new_fs_event()
watcher:start(vim.fs.dirname(path), {}, function(_, name)
	if name == vim.fs.basename(path) then
		vim.schedule(reload)
	end
end)

vim.o.autoread = true
vim.api.nvim_create_autocmd("FileChangedShell", {
	callback = function()
		vim.v.fcs_choice = "reload"
	end,
})

mdkite.start()

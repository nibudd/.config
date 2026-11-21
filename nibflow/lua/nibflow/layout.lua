local M = {}

local axes = {
	row = {
		split = "right",
		position = 2,
		get = vim.api.nvim_win_get_width,
		set = vim.api.nvim_win_set_width,
		fix = "winfixwidth",
	},
	col = {
		split = "below",
		position = 1,
		get = vim.api.nvim_win_get_height,
		set = vim.api.nvim_win_set_height,
		fix = "winfixheight",
	},
}

local function place(node, win)
	local placed = { node = node, win = win, children = {} }
	if node.view then
		return placed
	end
	local wins = { win }
	for i = 2, #node.children do
		local buf = vim.api.nvim_win_get_buf(wins[i - 1])
		wins[i] = vim.api.nvim_open_win(buf, false, { split = axes[node.split].split, win = wins[i - 1] })
	end
	for i, child in ipairs(node.children) do
		placed.children[i] = place(child, wins[i])
	end
	return placed
end

local function leaves(placed, found)
	found = found or {}
	if placed.node.view then
		table.insert(found, placed)
	end
	for _, child in ipairs(placed.children) do
		leaves(child, found)
	end
	return found
end

local function extent(placed, axis)
	local first, last = math.huge, 0
	for _, leaf in ipairs(leaves(placed)) do
		local start = vim.fn.win_screenpos(leaf.win)[axis.position]
		first = math.min(first, start)
		last = math.max(last, start + axis.get(leaf.win))
	end
	return last - first
end

local function fix(placed, axis)
	for _, leaf in ipairs(leaves(placed)) do
		vim.api.nvim_set_option_value(axis.fix, true, { win = leaf.win })
	end
end

local function size(placed)
	if placed.node.view then
		return
	end
	local axis = axes[placed.node.split]
	local total = extent(placed, axis)
	for _, child in ipairs(placed.children) do
		if child.node.cells then
			axis.set(child.win, child.node.cells)
			fix(child, axis)
		elseif child.node.percent then
			axis.set(child.win, math.floor(total * child.node.percent / 100 + 0.5))
		end
	end
	for _, child in ipairs(placed.children) do
		size(child)
	end
end

function M.build(layout, task_key)
	local root = place(layout.nvim, vim.api.nvim_get_current_win())
	size(root)
	for _, leaf in ipairs(leaves(root)) do
		require("nibflow.views." .. leaf.node.view).open(leaf.win, task_key)
	end
end

return M

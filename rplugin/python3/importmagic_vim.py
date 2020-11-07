import sys

import importmagic
import pynvim


@pynvim.plugin
class ImportMagicVim:
    def __init__(self, nvim):
        self.nvim = nvim
        self.index = importmagic.SymbolIndex()
        self.index_built = False
        self.update_source()
        # self.create_index([])

    @pynvim.function("CreateIndex")
    def create_index(self, _):
        a = self.nvim.command_output(
            "echo system('python -c \"import sys; print(sys.path)\"')"
        )
        self.nvim.out_write(a + "\n")
        self.index.build_index(eval(a))
        self.index_built = True

    def update_source(self, update=None):
        if not update:
            self.source = "\n".join(self.nvim.current.buffer[:])
        else:
            start, end, u = update
            tmp = self.source.splitlines()
            tmp[start:end] = u
            self.source = "\n".join(tmp)

    def get_update(self):
        self.update_source()
        scope = importmagic.Scope.from_source(self.source)
        unresolved, unreferenced = scope.find_unresolved_and_unreferenced_symbols()
        if unresolved or unreferenced:
            start_line, end_line, import_block = importmagic.get_update(
                self.source, self.index, unresolved, unreferenced
            )
            import_block = import_block.splitlines()[:-1]
            return start_line, end_line, import_block
        else:
            return None

    @pynvim.command("UpdateImports", nargs=0, sync=True)
    def testcommand(self):
        if not self.index_built:
            self.nvim.err_write("Index is not built yet\n")
        else:
            update = self.get_update()
            if update:
                start_line, end_line, import_block = update
                self.nvim.current.buffer[start_line:end_line] = import_block

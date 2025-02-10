class History:
    START = -1

    def __init__(self) -> None:
        self.rule_queue = []
        self.tail_ptr = self.START
        self.curr_ptr = self.START

    def push_rule(self, rule: str) -> None:
        self.rule_queue.insert(self.curr_ptr + 1, rule)
        self.tail_ptr += 1
        self.curr_ptr += 1

    def clear(self) -> None:
        self.rule_queue = []
        self.tail_ptr = self.curr_ptr = self.START

    def back(self) -> None:
        if self.curr_ptr != self.START:
            self.curr_ptr -= 1

    def forward(self) -> None:
        if not self.at_end:
            self.curr_ptr += 1

    def delete_current(self) -> None:
        if not self.at_beginning:
            self.rule_queue.pop(self.curr_ptr)
            self.tail_ptr -= 1

    def prune(self) -> None:
        next = self.curr_ptr + 1
        while next <= self.tail_ptr:
            self.rule_queue.pop(next)
            self.tail_ptr -= 1

    def print_out(self) -> list[str]:
        out = []
        for i, rule in enumerate(self.rule_queue):
            curr_prefix = "c-> " if self.curr_ptr == i else "       "
            out.insert(i, curr_prefix + rule)
        return out

    @property
    def at_end(self) -> bool:
        return self.tail_ptr == self.curr_ptr

    @property
    def at_beginning(self) -> bool:
        return self.curr_ptr == self.START

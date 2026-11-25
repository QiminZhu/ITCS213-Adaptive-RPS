# ============================================================================
# Adaptive Rock-Paper-Scissors - ITCS213
# Key Function: update(counts_base, ctx, move) + 1,000-move MARS Test Harness
#
# Register Interface for update():
#   $a0 = base address of counts[27] (27 aligned 32-bit words)
#   $a1 = ctx  (0..8, where ctx = 3 * prev_player + prev_computer)
#   $a2 = move (0..2, observed player move)
#   $t0 = pointer to current word in counts[]
#   $t3 = end address (&counts[27] = $a0 + 108)
# ============================================================================

.data
.align 2
counts:         .word 0:27              # 27 words (108 bytes), initialized to 0

msg_pass:       .asciiz "PASS: All 27 entries match Python exactly.\n"
msg_fail:       .asciiz "FAIL: Mismatches found = "
msg_table:      .asciiz "Final MIPS counts table:\n"
msg_space:      .asciiz " "
msg_newline:    .asciiz "\n"

# Pulls in num_moves, test_ctx[1000], test_move[1000], expected_counts[27]
.include "test_data.asm"

.text
.globl main

# ----------------------------------------------------------------------------
# Test Harness: replays all 1,000 (ctx, move) pairs and checks against Python
# ----------------------------------------------------------------------------
main:
    la    $s0, num_moves
    lw    $s0, 0($s0)                   # $s0 = 1000
    addu  $s1, $zero, $zero             # $s1 = loop index i = 0
    la    $s2, test_ctx                 # $s2 = &test_ctx[0]
    la    $s3, test_move                # $s3 = &test_move[0]
    la    $s4, counts                   # $s4 = &counts[0]

replay_loop:
    addu  $a0, $s4, $zero               # arg 0: base address of counts
    lw    $a1, 0($s2)                   # arg 1: test_ctx[i]
    lw    $a2, 0($s3)                   # arg 2: test_move[i]
    jal   update                        # call update(counts, ctx, move)

    addiu $s2, $s2, 4                   # next test_ctx word
    addiu $s3, $s3, 4                   # next test_move word
    addiu $s1, $s1, 1                   # i++
    bne   $s1, $s0, replay_loop

    # --- Compare counts[0..26] against expected_counts[0..26] ---
    la    $t0, counts                   # pointer to MIPS result
    la    $t1, expected_counts          # pointer to Python reference
    addiu $t2, $zero, 27                # 27 entries to check
    addu  $s5, $zero, $zero             # $s5 = mismatch counter

verify_loop:
    lw    $t3, 0($t0)
    lw    $t4, 0($t1)
    beq   $t3, $t4, match_ok
    addiu $s5, $s5, 1                   # mismatch++

match_ok:
    addiu $t0, $t0, 4
    addiu $t1, $t1, 4
    addiu $t2, $t2, -1
    bne   $t2, $zero, verify_loop

    # --- Print PASS or FAIL ---
    bne   $s5, $zero, print_fail
    li    $v0, 4
    la    $a0, msg_pass
    syscall
    j     print_table

print_fail:
    li    $v0, 4
    la    $a0, msg_fail
    syscall
    li    $v0, 1
    addu  $a0, $s5, $zero
    syscall
    li    $v0, 4
    la    $a0, msg_newline
    syscall

    # --- Print final 27-word counts table ---
print_table:
    li    $v0, 4
    la    $a0, msg_table
    syscall

    la    $t0, counts
    addiu $t1, $zero, 27

print_loop:
    li    $v0, 1
    lw    $a0, 0($t0)
    syscall
    li    $v0, 4
    la    $a0, msg_space
    syscall
    addiu $t0, $t0, 4
    addiu $t1, $t1, -1
    bne   $t1, $zero, print_loop

    li    $v0, 4
    la    $a0, msg_newline
    syscall

    li    $v0, 10                       # exit
    syscall

# ----------------------------------------------------------------------------
# KEY FUNCTION: update(counts_base, ctx, move)
#   for i in range(27):
#       counts[i] -= counts[i] >> 3
#   counts[3 * ctx + move] += 16
#
# Exact dynamic instruction count per call:
#   2 (setup) + 27 * 6 (decay loop) + 9 (increment & return) = 173 instructions
# ----------------------------------------------------------------------------
update:
    addu  $t0, $a0, $zero               # $t0 = &counts[0]
    addiu $t3, $a0, 108                 # $t3 = &counts[27] (27 * 4 bytes)

decay_loop:
    lw    $t1, 0($t0)                   # $t1 = counts[i]
    srl   $t2, $t1, 3                   # $t2 = counts[i] >> 3
    subu  $t1, $t1, $t2                 # $t1 = counts[i] - (counts[i] >> 3)
    sw    $t1, 0($t0)                   # counts[i] = $t1
    addiu $t0, $t0, 4                   # next word (+4 bytes)
    bne   $t0, $t3, decay_loop          # repeat until $t0 == &counts[27]

    # Compute &counts[3 * ctx + move] = $a0 + 4 * ((ctx << 1) + ctx + move)
    sll   $t4, $a1, 1                   # $t4 = 2 * ctx
    addu  $t4, $t4, $a1                 # $t4 = 3 * ctx
    addu  $t4, $t4, $a2                 # $t4 = 3 * ctx + move
    sll   $t4, $t4, 2                   # $t4 = 4 * (3 * ctx + move)
    addu  $t4, $a0, $t4                 # $t4 = &counts[3 * ctx + move]

    lw    $t5, 0($t4)                   # load target entry
    addiu $t5, $t5, 16                  # add INCREMENT (16)
    sw    $t5, 0($t4)                   # store updated entry
    jr    $ra                           # return to caller

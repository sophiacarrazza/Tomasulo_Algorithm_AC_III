test_cases = {
    'raw_hazard': [
        "LW R1, 0(R2)",
        "ADD R3, R1, R4",
        "MUL R5, R3, R6"
    ],
    'branch_test': [
        "BEQ R1, R2, Label",
        "ADD R3, R4, R5",
        "Label: SUB R6, R7, R8"
    ]
}

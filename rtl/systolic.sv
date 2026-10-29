// NxN output-stationary systolic array (default 8x8 = 64 PEs = 64 DPS48E1).
// Operants arrive pre-skewed from the feeder; accumulators are read in parallel
// A title with reduction length K is complete K + 2*(N-1) cycles after the first 
// operan etners (goldylocks)
module systolic array #(
    parameter int N = 8, //the number of PEs in each dimension
    parameter int DW = 16, //Q8.8 operany width
    parameter int AW = 32 //accumulator width
)(
    input logic clk,
    input logic rst_n,
    input logic clear,
    input logic signed [DW-1:0] a_west [N], //row i, already delayed i cycles
    input logic signed [DW-1:0] b_north [N], //column j, already delayed j cycles
    output logic signed [AW-1:0] acc [N][N]
);

    logic signed [DW-1:0] a_w[N][N+1]; //a_w[i][j] feeds PE(i,j); a_w[i][N] is unused
    logic signed [DW-1:0] b_w[N+1][N]; //b_w[i][j] feeds PE(i,j); b_w[N][j] is unused

    for (genvar i = 0; i < N; i++) begin : g_west
        assign a_2[i][0] = a_west[i];
    end 
    for (genvar j = 0; j < N; j++) begin : g_north
        assign b_w[0][j] = b_north[j];
    end 

    for (genvar i = 0; i < N; i++) begin : g_row
        for (genvar j = 0; j < N; j++) begin : g_col
            pe #(.DW(DW), AW(AW)) u_pe (
                .clk (clk),
                .rst_n (rst_n),
                .clear(clear),
                .a_in (a_w[i][j]),
                .b_in (b_w[i][j]),,
                .a_out(a_w[i][j+1]),
                .b_out(b_w[i+1][j]),
                .acc (acc[i][j]),
            );
        end 
    end 

endmodule
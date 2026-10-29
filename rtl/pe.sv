//Output stationary processing element
// acc <= acc + a_in * b_in every cycle (accumulator stays in the PE)
// a flows west->east, b flows north0->south, one register per hop

// Contract with feeder (goldylocks is the reference model)
(* use_dsp = "yes" *)
module pe #(
    parameter int DW = 16, //Q8.8 operand width
    parameter int AW = 32  //accumulator width
) (
    input logic clk,
    input logic rst_n, //synchronous active low reset
    input logic clear,
    input logic signed [DW-1:0] a_in,
    input logic signed [DW-1:0] b_in,
    output logic signed [DW-1:0] a_out,
    output logic signed [DW-1:0] b_out,
    output logic signed [AW-1:0] acc
);

    logic signed [2*DW- 1:0] prod;
    assign prod = a_in * b_in;

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            a_out <= '0;
            b_out <= '0;
            acc <= '0;
        end else begin
            a_out <= a_in;
            b_out <= b_in;
            if (clear) acc <= '0;
            else acc <= acc + prod;
        end 
    end 

endmodule 
; ==============================================================
; Prusa Mini - Bed Perimeter Sweep
; Board: Duet (RRF firmware)
; Purpose: Move hotend around the perimeter of the print area
;          at slightly above first layer height (~0.3mm).
;          No extrusion.
; Bed size: 180 x 180 mm (Prusa Mini)
; ==============================================================

; --- Startup / Safety ---
G21              ; Set units to millimetres
G90              ; Absolute positioning
M104 S0          ; Hotend heater off
M140 S0          ; Bed heater off
M107             ; Fan off

; --- Home all axes ---
G28

; --- Lift to safe Z before XY travel ---
G1 Z5 F3000

; --- Move to start position (front-left) ---
G1 X5 Y5 F6000

; --- Drop to sweep height: 0.3mm ---
G1 Z0.3 F1200

; --- Perimeter loop x3 ---
G1 X175 Y5   F3000
G1 X175 Y175 F3000
G1 X5   Y175 F3000
G1 X5   Y5   F3000

G1 X175 Y5   F3000
G1 X175 Y175 F3000
G1 X5   Y175 F3000
G1 X5   Y5   F3000

G1 X175 Y5   F3000
G1 X175 Y175 F3000
G1 X5   Y175 F3000
G1 X5   Y5   F3000

; --- Lift and park ---
G1 Z10 F3000
G1 X5 Y5 F6000

M117 Perimeter sweep complete.

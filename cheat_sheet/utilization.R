setwd("~/git/homebrew/cheat_sheet")

rm(list = ls())

df = read.csv("utilization.csv")
m = as.matrix(df)
s = paste0("\\begin{tabular}{cc|c|", paste(rep("c", ncol(df) - 2), collapse = ""), "}\n",
           paste0("& & \\multicolumn{", ncol(df) - 1, "}{c}{Gravity}\\\\\n"),
           paste0("& & ", paste(gsub("^X", "", names(df)[-1]), collapse = " & ")), "\\\\ \\hline\n",
           paste0("\\multirow{", nrow(df), "}{*}{\\rotatebox[origin=c]{90}{Time (minutes)}} ", paste(sapply(1:nrow(m), function(i) paste0("& ", paste(m[i,], collapse = " & "), "\\\\\n")), collapse = "")),
           "\\hline\\hline\n\\end{tabular}"
)
cat(s)

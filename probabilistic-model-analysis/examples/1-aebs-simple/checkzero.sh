model="configurations/$1/"
bcg_open $model"simple-final-pts.bcg" exhibitor -case -dfs -all <<< "<until> [.*; prob 0]"
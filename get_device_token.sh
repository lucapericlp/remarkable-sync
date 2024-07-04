for log in "$(find "/Users/lucaperic/Library/Application Support/Google/Chrome/Default/Local Extension Settings/bfhkfdnddlhfippjbflipboognpdpoeh" -iname '*.log')"; do
  strings "${log}" | grep -1 deviceToken | cut -d '"' -f2
  # strings "${log}"
done

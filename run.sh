#!/bin/bash
while [ "$#" -gt 0 ]; do
  case $1 in
    --ai-settings)
      ai_settings="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

python scripts/check_requirements.py requirements.txt
if [ $? -eq 1 ]
then
    echo Installing missing packages...
    pip install -r requirements.txt
fi

if [ -n "$ai_settings" ]; then
  python -m autogpt --ai-settings "$ai_settings"
else
  python -m autogpt
fi

read -p "Press any key to continue..."

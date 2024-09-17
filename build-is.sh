oc new-build --name cvision-browser --strategy docker --binary --context-dir .
oc start-build cvision-browser --from-dir cvbrowser --follow


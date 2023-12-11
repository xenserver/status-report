.RECIPEPREFIX=>
darker-xen-bugtool:
>@ pip install 'darker[isort]'
>@ tmp=`mktemp`                                       ;\
>  darker --stdout --isort -tpy36 xen-bugtool >$$tmp ||\
>    exit 5                                           ;\
>  diff -u xen-bugtool $$tmp                          ;\
>  if [ $$? != 0 ]; then cat $$tmp >xen-bugtool       ;fi
>@ rm -f $$tmp

from goods.models import GoodsCategory

def get_breadcrumb(category):
    # 只有一级：breadcrumb = {cat1 ：''}
    # 只有二级：breadcrumb = {cat1 ：''，cat2 ：''}
    # 只有三级：breadcrumb = {cat1 ：''，cat2 ：''，cat3 ：''}

    breadcrumb = {
        'cat1':'',
        'cat2':'',
        'cat3':''
    }
    if category.parent == None:
        # 说明是一级的导航栏
        breadcrumb['cat1'] = category
    elif GoodsCategory.objects.filter(parent_id=category.id).count() == 0:
        # 三级
        cat2 = category.parent
        breadcrumb['cat1'] = cat2.parent
        breadcrumb['cat2'] = cat2
        breadcrumb['cat3'] = category
    else:
        breadcrumb['cat1'] = category.parent
        breadcrumb['cat2'] = category

    return breadcrumb
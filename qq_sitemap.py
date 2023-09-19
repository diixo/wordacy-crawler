
from usp.tree import sitemap_tree_for_homepage

def main():
   tree = sitemap_tree_for_homepage('https://www.programiz.com')
   #tree = sitemap_tree_for_homepage('https://www.techopedia.com')

   counter = 0;
   for page in tree.all_pages():
      counter += 1
      #print(page)

   print(f"sz={counter}")

##########################
if __name__ == "__main__":
    main()

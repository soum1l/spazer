# spazer
DCBD 2023 Assignment 1

We utilize the structure of the HTML tree to extract potential addresses. All the preprocessing steps act directly upon the HTML tree generated by BeautifulSoup4.

Preprocessing steps (in order):

- HTML tags that cannot contain text, along with comments, are deleted.
- Tags with no text underneath them are deleted.
- Tags which provide no additional structural information, i.e. tags with a single non textual child, are replaced by its only child.
- To homogenize the structure of the Tree, we wrap any naked text, i.e. text with at least one sibling that is a HTML tag, is wrapped inside a <div>...</div>.

Since the above operations were performed in a top to bottom fashion, the resultant HTML tree will possess the following properties:

1. A node is a text <===> it is a leaf.
2. Every non-leaf has children that are either all text or all tags.
3. Every non-leaf that is not the parent of a leaf, has at least 2 children.

Address identification:

We assume the following, in context of an address:

- It must have either a 6 digit number (zip code) or the name of a City/Village/District/State.
- The whole address (including email and phone) has around 70 words in total.
- The whole address resides within the tree rooted at the parent of the tag in which the zipcode/name of district is found.

The steps are outlined below:

1. Clear out the class attribute of every tag. This will be used to mark the desirable tags.
2. Iterate over the nodes whose children are leaves, and match each n-gram obtained from the strings under the node with an external database consisting of Indian Localities, and if not matched, with a RegEx for zipcode.
3. If a match is obtained, mark the tag with a '@'.
4. Start marking the tags around the matched tag until we run out of tags, or hit the total word count threshold.
4. Delete the leaves whose parent was not marked in the final step.

Postprocessing steps:

- Remove excessive whitespaces and newlines.

#Spazer tool for processing web pages
#

from bs4 import BeautifulSoup
import pathlib

#Variables to track the input, output and gained space
space_gained = 0
space_input = 0
space_output = 0

print("Welcome to Spazer\n")

for x in range(10):
    filename = str(x) + ".html"
    file = pathlib.Path('input/' + filename)
    if (file.exists()):

        #Read each file
        print("Reading " + filename)
        f = open('input/' + filename, 'r', errors="ignore")
        contents = f.read()

        #Remove html tags
        soup = BeautifulSoup(contents, 'lxml')
        output = soup.get_text()

        #Your code begins  ###############################

        ### Simplifying the HTML Tree [PREPROCESSING] ####################

        #Load list of Non-Textual HTML tags
        fa = open('data/UselessTags.txt', 'r', errors="ignore")
        useless_tags = fa.read().strip().split('\n')
        fa.close()

        #Remove Non-Textual HTML tags
        for tag in soup.find_all(name=useless_tags):
            _ = tag.extract()

        #Remove html comments
        from bs4 import Comment
        for comment in soup.find_all(string=lambda s: isinstance(s,Comment)):
            _ = comment.extract()

        #Remove empty tags
        for tag in soup.find_all():
            if len(tag.get_text(strip=True)) == 0:
                _ = tag.extract()

        #Remove superfluous tags (Preserve root)
        for tag in soup.find_all()[1:]:
            if len(tag.find_all(recursive=False)) == 1:
                tag.unwrap()

        #Wrap naked text in divs
        for tag in soup.find_all():
            if len(tag.find_all(recursive=False)) > 0:
                for chunk in tag.find_all(string=True, recursive=False):
                    if len(chunk.strip()) > 0:
                        chunk.wrap(soup.new_tag('div'))

        ### Each Leaf is a Token (guaranteed to be non-empty text!) ######

        ### Process further, under the assumption that every #############
        ### Token is a valid address/e-mail/telephone-number #############

    	#Load database of Indian Cities and Villages
        fb = open('data/Localities.min.txt', 'r', errors="ignore")
        localities = fb.read().strip().split('\n')
        fb.close()

        #Empty out class attribute
        for tag in soup.find_all():
            tag['class'] = None

        #Mark chunks (and its siblings) containing Indian addresses
        import re
        from bisect import bisect_left as bisect
        wc_thres = 70
        for tag in soup.find_all():
            for chunk in tag.find_all(string=True, recursive=False):
                chunk = re.sub('[^A-Za-z0-9]+', ' ', chunk).lower().split()
                for i in range(len(chunk)):
                    matched = False
                    for j in range(len(chunk)-i):
                        token = ' '.join(chunk[j:j+i+1])
                        index = bisect(localities, token)
                        if (    # locality in database
                                (index != len(localities) and localities[index] == token)
                                # zip code
                             or (re.match('^\d{6}$', token))
                           ):
                            tag['class'] = '@'
                            #Get surrounding tags under parent node
                            u_lines = list(filter(lambda t: t in tag.parent.find_all(), tag.find_all_previous()))
                            l_lines = list(filter(lambda t: t in tag.parent.find_all(), tag.find_all_next()))
                            #Traverse in a spiral fashion
                            lines = [item for sublist in zip(u_lines, l_lines) for item in sublist]
                            lines += u_lines[len(l_lines):] + l_lines[len(u_lines):]
                            wc = len(chunk)
                            for line in lines:
                                if wc > wc_thres: break
                                line_chunk = ' '.join(line.find_all(string=True, recursive=False))
                                line_chunk = re.sub('[^A-Za-z0-9]+', ' ', line_chunk).strip().split()
                                line['class'] = '@'
                                wc += len(line_chunk)
                            matched = True
                            break
                    if matched: break

        #Delete unmarked Leaves
        for tag in soup.find_all():
            if len(tag.find_all(recursive=False)) != 0:
                continue
            if tag['class'] is None:
                _ = tag.extract()

        ### Editing resultant string [POSTPROCESSING] ####################

        #Strip spaces and remove excessive newlines
        output = soup.get_text().strip()
        output = re.sub('\s{2,}', ' ', output)
        output = re.sub('[\n\t]?', '', output)
        #Your code ends  #################################

        #Write the output variable contents to output/ folder.
        print ("Writing reduced " + filename)
        fw = open('output/' + filename, "w")
        fw.write(output)
        fw.close()
        f.close()

        #Calculate space savings
        space_input = space_input + len(contents)
        space_output = space_output + len(output)

space_gained = round((space_input - space_output) * 100 / space_input, 2)

print("\nTotal Space used by input files = " + str(space_input) + " characters.")
print("Total Space used by output files = " + str(space_output) + " characters.")
print("Total Space Gained = " + str(space_gained) + "%")

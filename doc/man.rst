=========
svgplease
=========

--------------------------------------
manipulate svg images from commandline
--------------------------------------

:Author: Michał Sapalski <sapalskimichal@gmail.com>
:Date: 2014-05-23
:Copyright: GPLv3
:Version: 0.2
:Manual section: 1
:Manual group: image processing

SYNOPIS
=======
  
svgplease [--complete] commands

DESCRIPTION
===========

svgplease performs simple operations on svg images. It uses an English-like language to specify the operations. Available commands are described in the COMMANDS section below. Commands can be chained using the "then" keyword.

The commands work in the following way:
  * svgplease keeps list of currently opened files and currently selected nodes
  * commands can read currently opened files and modify selected nodes (or other nodes, relative to the selected ones)
  * commands can open/close files and change selection

EXAMPLE
=======

svgplease open input.svg then select '#a-circle' then set fill color to '#ff0000' then save to output.svg

This performs the following operations:
  * the 'input.svg' file is opened
  * an svg element with id 'a-circle' is selected
  * it's fill color is set to red (#ff0000)
  * the result is saved to file 'output.svg'

Note that '#' has to be quoted so that the shell doesn't treat it as a comment.

See the COMMANDS sections for more examples. 

COMMANDS
========

**open** FILE_NAME [FILE_NAME...]

  Opens given files and selects their top-level <svg> element. File names can be prefixed with a 'file' keyword to avoid treating file name as a keyword. This is useful if your file is named like one of the commands, but usually not needed.

  Example:
    svgplease **open** file foo.svg bar.svg then save to foo_copy.svg bar_copy.svg

    Effectively copies foo.svg and bar.svg to foo_copy.svg and bar_copy.svg.

**save** [to] FILE_NAME [FILE_NAME...]

  Saves currently opened files using given file names. If there are more open files than file names, new file names will be generated. See **open** command for more information about file names and an example of usage.

**select** #node_id

  Replaces each currently selected node by it's descendant with id node_id. Note that '#' should be quoted so that the shell doesn't interpret it as a comment.

  Example:
    svgplease open foo.svg then **select** '#foo' then scale by 2 then save to bar.svg

    Makes the node with id 'foo' in the file 'foo.svg' twice as big and saves result to 'bar.svg'

**remove** [selected]

  Removes all currently selected nodes.

  Example:
    svgplease open foo.svg then select '#foo' then **remove** selected then save to bar.svg

    Remove node with id 'foo' from file 'foo.svg' and save result to 'bar.svg'

**move** [by] DISPLACEMENT [[and by] DISPLACEMENT] 

**move** [by] DISPLACEMENT DIRECTION [[and by] DISPLACEMENT [DIRECTION]]

  Moves selected nodes horizontally and vertically. DISPLACEMENT could be any number followed by one of units: pixel (px), point (pt), millimeter (mm), centimeter (cm). The default unit is pixel. Plural form of units (e.g. 'pixels') are also supported. DIRECTION is one of: vertically (ver, y), horizontally (hor, x). The default directions are: first horizontally, then vertically.

  Examples:
    svgplease open foo.svg then select '#foo' then **move** by -32mm horizontally and by 10 pixels vertically then save to bar.svg

    svgplease open foo.svg then select '#foo' then **move** 10px -32mm then save bar.svg

    These two commands do the same thing: move node with id 'foo' in file 'foo.svg' 10 pixels to the right and 32 millimeters up and save result to 'bar.svg'

**scale** [by] SCALE [DIRECTION] [[and by] SCALE [DIRECTION]]

  Scales selected nodes by SCALE. SCALE can be expressed as a number or percentage (note that '%' sign should be quoted so that the shell doesn't expand it). DIRECTION can be specified to scale horizontally and/or vertically by different amount. See **move** command for more information about specifying directions. Default directions are: both (when one number is given) or first horizontally, then vertically.

  Examples:

    svgplease open foo.svg then select '#foo' then **scale** by 1.5 horizontally and by '150%' vertically then save to bar.svg

    svgplease open foo.svg then select '#foo' then **scale** 1.5 then save to bar.svg

    These two commands do the same thing: open file 'foo.svg', select node with id 'foo', scale it by 150% horizontally and vertically and save to 'bar.svg'

**change** [fill] [[and] stroke] [color] [to] #rrggbb[aa]

**change** [fill] [[and] stroke] [color] [from] #rrggbb[aa] [to] #rrggbb[aa]
  
  Changes fill and/or stroke color of the selected nodes and all their descendants to given one. The second variant of the command changes color from one color to another -- nodes having different colors are left unchanged. If alpha component is specified, opacity is also set. Note that '#' has to be escaped so that the shell doesn't interpret it as a comment.

  Examples:

    svgplease open foo.svg then select '#foo' then **change** fill and stroke color from '#ff0000' to '#00ff0088' then save to bar.svg

    svgplease open foo.svg then select '#foo' then **change** '#ff0000' '#00ff0088' then save to bar.svg

    These two commands do the same thing: change fill and stroke color for nodes that are descendants of the node with id 'foo' from file 'foo.svg' if their current color is red (#ff0000). The target color is half-transparent blue (#00ff0088). The result is saved to 'bar.svg'.

**change** font [family] to FONT

  Changes font of all selected text nodes and their descendands to given.

  Examples:
    
    svgplease open foo.svg then **change** font family to 'Times New Roman' then save to bar.svg

    This command sets the font for all the text in 'foo.svg' to 'Times New Roman'. The result is saved to 'bar.svg'.

**change** font size [to] SIZE

  Changes font size of all selected text nodes and their descendands to given.
  
  Examples:
    
    svgplease open foo.svg then **change** font size to 15px then save to bar.svg

    This command will set font size for all the text in 'foo.svg' to 15 pixels and save the result to 'bar.svg'.

**change like** [from] FILENAME [via FILENAME...] [to] FILENAME

  Detects changes that were made between two (or more) files and applies them to currently opened files.
  See *change_detection_algorithm.txt* (https://github.com/sapal/svgplease/blob/master/doc/change_detection_algorithm.txt) for explanation how the changes are detected.

  Examples:

    svgplease open color.svg then **change like** from base.svg to move.svg then save to merged.svg

    Let's say that we have file 'base.svg' and we modified it in two different ways: we changed color of some nodes and saved it to 'color.svg', then reopened 'base.svg', moved some (possibly the same) nodes around and saved to 'move.svg'. By using this command we obtain 'merged.svg' in which all changes are present: some nodes have changed color and some are moved.

    svgplease open base.svg then **change like** from file1.svg via file2.svg via file3.svg to file4.svg then save to result.svg

    Opens file 'base.svg', then applies all the changes between 'file1.svg' and 'file2.svg', then applies the changes between 'file2.svg' and 'file3.svg', changes between 'file3.svg' and 'file4.svg' and saves the result to 'result.svg'.

**change text** to SOME_TEXT

  Changes the text in all selected nodes (and their descendants) to the given text.

  Examples:

    svgplease open foo.svg then select '#foo' then **change text** to 'LOL' then save to bar.svg

    Change the text in node '#foo" from file 'foo.svg' to 'LOL' and save the result to 'bar.svg'.

**tile** [on] PAGE_SPECIFICATION [page[s]]
**tile** [to fill] PAGE_SPECIFICATION [page[s]]
    
  Puts opened files onto a page (or multiple pages) of given size. If 'to fill' option is specified, opened files are repeated untill exactly one page is filled.
  PAGE_SPECIFICATION can be:

     * a constant like: a3, a4, a5
     * width and height: '10cm by 15cm' or '500 300'

  Examples:

    svgplease open foo1.svg foo2.svg foo3.svg then **tile** on a4 page then save to bar.svg

    svgplease open foo1.svg foo2.svg foo3.svg then **tile** on 210mm by 297mm page then save to bar.svg

    These two commands do the same: open files 'foo1.svg' 'foo2.svg' 'foo3.svg' and tries to put them on one A4 page (if that's impossible, they will be put onto two or three pages). The output is saved to 'bar.svg'.

OPTIONS
=======

--complete    Instead of executing the commands, suggest the next word. This option is for implementing tab-completion in shell.


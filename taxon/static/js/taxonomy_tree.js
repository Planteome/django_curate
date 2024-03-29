function build_tree(taxons) {
    // Loop through all taxons and put them in order by parentage
    let dataMap = {};
    taxons.forEach(function(node) {
        dataMap[node.ncbi_id] = node;
    });
    // create the tree array
    let tree = [];
    taxons.forEach(function(node) {
        // skip the root term
        if (node['parent'] === 0) {
            return;
        }
        // find parent until "cellular organisms" which has parent root with ncbiID == 1
        if (node['parent'] !== 1) {
            let parent = dataMap[node['parent']];
            // create child array if it doesn't exist
            (parent.children || (parent.children = []))
                // add node to parent's child array
                .push(node);
        } else {
            // top level, root term
            tree.push(node);
        }
    });
    // Send to function to add the html
    return tree_to_html(tree, true);
}

function tree_to_html(tree, first) {
    let htmlText = '';
    tree.forEach(function(node) {
        if(first) {
            htmlText += '<ul id="accordion">';
        }
        // TODO: pretty up this text some more
        const nodeID = (node.name).replace(/\s/g, '').replace(/\//g, '')
        htmlText += '<li class="taxonElement" id="' + nodeID + '"><a href="/taxon/' + node.ncbi_id + '">' + node.name + '</a>';
        if(node.num_genes > 0) {
            htmlText += " - " + '<a href="/gene/by-taxon/' +node.ncbi_id + '">' + node.num_genes + "</a> genes";
        }
        if(node.num_annotations > 0) {
            htmlText += " - " + '<a class="annotationLink" href="/annotations/by-taxon/' + node.ncbi_id + '">' + node.num_annotations + "</a> annotations";
        } else {
            htmlText += '<span class="annotationCount"></span>'
        }
        if(node.children) {
            htmlText += '<i class="fa fa-plus fa-xs" style="line-height: 24px; font-size: 12px; float: right; margin-right: 25px"></i>'
            htmlText += '<ul>' + tree_to_html(node.children, false) + '</ul>';
        }

        if(first) {
            htmlText += '</ul>';
        }
    });
    return htmlText;
}

// function to calculate and update the depth of all taxonomy elements
function update_depth(openLevelVar) {
    const max_depth = 12;
    const max_color = 200;
    $('.taxonElement').each(function(index, element) {
        const depth = $(this).parentsUntil("#taxonomy_tree", 'ul').length;
        // Set the initial icon to a minus if depth less/equal than openLevelVar (set it taxon_display.html)
        if(depth <= openLevelVar) {
            $(this).children('i').first().toggleClass("fa-plus fa-minus");
        }
        // Make it just alternate colors after max_depth
        let new_opacity;
        if(depth < max_depth) {
            new_opacity = Math.round(max_color * (depth - 1) / max_depth);
        } else if(depth % 2 === 0) {
            new_opacity = Math.round(max_color * (max_depth) / max_depth);
        } else{
            new_opacity = Math.round(max_color * (max_depth - 4) / max_depth);
        }
        element.style.background = LightenDarkenColor("#f0ad4e", new_opacity);
    });
}

// function to lighten or darken hex colors
// Taken from https://css-tricks.com/snippets/javascript/lighten-darken-color/
function LightenDarkenColor(col, amt) {
    let usePound = false;
    if (col[0] === "#") {
        col = col.slice(1);
        usePound = true;
    }
    let num = parseInt(col,16);
    let r = (num >> 16) + amt;
    if (r > 255) r = 255;
    else if (r < 0) r = 0;

    let b = ((num >> 8) & 0x00FF) + amt;
    if (b > 255) b = 255;
    else if (b < 0) b = 0;

    let g = (num & 0x0000FF) + amt;

    if (g > 255) g = 255;
    else if (g < 0) g = 0;

    return (usePound?"#":"") + (g | (b << 8) | (r << 16)).toString(16);
}
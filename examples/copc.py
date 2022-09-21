from laspy import CopcReader, Bounds
import time
import laspy

from laspy.copc import load_octree_for_query
from operator import attrgetter

def create_query(header):
    querys = []

    sizes = header.maxs - header.mins

    # Bottom left
    query_bounds = Bounds(
        mins=header.mins,
        maxs=header.mins + sizes / 2
    )
    query_bounds.maxs[2] = header.maxs[2]
    querys.append(query_bounds)

    # Top Right
    # Bounds can also be 2D (then all Z are considered)
    query_bounds = Bounds(
        mins=(header.mins + sizes / 2)[:2],
        maxs=header.maxs[:2]
    )
    querys.append(query_bounds)


    return querys


def multi_query(header, bounds_list):


    pass

def main():
    path = "http://192.168.1.110:9000/geospatial/copc/lidar_sample.copc.laz"
    
    with CopcReader.open(path) as crdr:
        print("copc_reader_ready")
        querys = create_query(crdr.header)

        # points = crdr.query(querys[0], resolution=None)

        for query in querys:
            query = query.ensure_3d(crdr.header.mins, crdr.header.maxs)
            t0 = time.time()
            octree = load_octree_for_query(crdr.source, crdr.copc_info, crdr.root_page, query, None)

            nodes_to_read = sorted(octree, key=attrgetter("offset"))
            grouped_nodes = []
            current_group = []
            last_node_end = nodes_to_read[0].offset
            for node in nodes_to_read:
                if node.offset == last_node_end:
                    current_group.append(node)
                    last_node_end += node.byte_size
                else:
                    grouped_nodes.append(current_group)
                    current_group = [node]
                    last_node_end = node.offset + node.byte_size
            if current_group:
                grouped_nodes.append(current_group)
            t1 = time.time()
            print(t1 - t0)

        # multi_query(crdr.header, querys)

        # for i, query_bounds in enumerate(querys):
        #     resolution = None
        #     points = crdr.query(query_bounds, resolution=resolution)
        #     print("Spatial Query gave:", points)
        #     print(len(points) / crdr.header.point_count * 100);

        #     new_header = laspy.LasHeader(
        #         version=crdr.header.version,
        #         point_format=crdr.header.point_format
        #     )
        #     new_header.offsets = crdr.header.offsets
        #     new_header.scales = crdr.header.scales
        #     with laspy.open(f"output_{i}.las", mode="w", header=new_header) as f:
        #         f.write_points(points)



if __name__ == '__main__':
    t0 = time.time()
    main()
    t1 = time.time()
    print("It took:", t1 - t0, " seconds")


import asyncio
import sys
import time

import serial_read
from base64 import b64encode
from traceback import print_exception
from typing import Set, Type
from foxglove_websocket import run_cancellable
from foxglove_websocket.server import FoxgloveServer, FoxgloveServerListener

try:
    from foxglove_schemas_protobuf.SceneUpdate_pb2 import SceneUpdate
    from foxglove_schemas_protobuf.Vector3_pb2 import Vector3
    from foxglove_schemas_protobuf.FrameTransforms_pb2 import FrameTransforms
    from foxglove_schemas_protobuf.ArrowPrimitive_pb2 import ArrowPrimitive
    from foxglove_websocket.types import ChannelId, ChannelWithoutId

    from google.protobuf.wrappers_pb2 import BoolValue
    import google.protobuf.message
    from google.protobuf.descriptor_pb2 import FileDescriptorSet
    from google.protobuf.descriptor import FileDescriptor
except ImportError as _:
    print_exception(*sys.exc_info())
    print(
        "unable to import protobuf schemas; did you forget to run `pip install 'foxglove-websocket[examples]'`?",
    )
    sys.exit(1)


def build_file_descriptor_set(
    message_class: Type[google.protobuf.message.Message],
) -> FileDescriptorSet:
    """
    Build a FileDescriptorSet representing the message class and its dependencies.
    """
    file_descriptor_set = FileDescriptorSet()
    seen_dependencies: Set[str] = set()

    def append_file_descriptor(file_descriptor: FileDescriptor):
        for dep in file_descriptor.dependencies:
            if dep.name not in seen_dependencies:
                seen_dependencies.add(dep.name)
                append_file_descriptor(dep)
        file_descriptor.CopyToProto(file_descriptor_set.file.add())  # type: ignore

    append_file_descriptor(message_class.DESCRIPTOR.file)
    return file_descriptor_set


async def main():
    class Listener(FoxgloveServerListener):
        async def on_subscribe(self, server: FoxgloveServer, channel_id: ChannelId):
            print("First client subscribed to", channel_id)

        async def on_unsubscribe(self, server: FoxgloveServer, channel_id: ChannelId):
            print("Last client unsubscribed from", channel_id)

    async with FoxgloveServer("0.0.0.0", 8765, "example server") as server:

        reader = serial_read.AsyncSerialReader("/dev/cu.usbmodem9888E00715142", 230400)
        server.set_listener(Listener())

        tfs_id = await server.add_channel(
            {
                "topic": "tfs",
                "encoding": "protobuf",
                "schemaName": FrameTransforms.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(FrameTransforms).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )

        worldview_id = await server.add_channel(
            {
                "topic": "worldview",
                "encoding": "protobuf",
                "schemaName": SceneUpdate.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(SceneUpdate).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )

        is_stance_id = await server.add_channel(
            {
                "topic": "isStance",
                "encoding": "protobuf",
                "schemaName": BoolValue.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(BoolValue).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )

        a_m_id = await server.add_channel(
            {
                "topic": "a_m",
                "encoding": "protobuf",
                "schemaName": Vector3.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(Vector3).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )

        a_w_id = await server.add_channel(
            {
                "topic": "a_w",
                "encoding": "protobuf",
                "schemaName": Vector3.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(Vector3).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )

        a_b_id = await server.add_channel(
            {
                "topic": "a_b",
                "encoding": "protobuf",
                "schemaName": Vector3.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(Vector3).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )

        v_id = await server.add_channel(
            {
                "topic": "velocity",
                "encoding": "protobuf",
                "schemaName": Vector3.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(Vector3).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )

        fa_id = await server.add_channel(
            {
                "topic": "fa",
                "encoding": "protobuf",
                "schemaName": Vector3.DESCRIPTOR.full_name,
                "schema": b64encode(
                    build_file_descriptor_set(Vector3).SerializeToString()
                ).decode("ascii"),
                "schemaEncoding": "protobuf",
            }
        )

        i = 0
        while True:
            i += 1
            payload = await reader.read_packet()

            a_w = Vector3()
            a_w.x = payload.a_w[0]
            a_w.y = payload.a_w[1]
            a_w.z = payload.a_w[2]

            print("got packet! aw = %f", payload.a_w[0])

            a_b = Vector3()
            a_b.x = payload.a_b[0]
            a_b.y = payload.a_b[1]
            a_b.z = payload.a_b[2]

            v = Vector3()
            v.x = payload.v[0]
            v.y = payload.v[1]
            v.z = payload.v[2]


            now = time.time_ns()

            scene_update = SceneUpdate()
            entity = scene_update.entities.add()
            entity.timestamp.FromNanoseconds(now)
            entity.id = "debug_imu_cube"
            entity.frame_id = "imu"
            cube = entity.cubes.add()
            cube.size.x = 0.05
            cube.size.y = 0.05
            cube.size.z = 0.05
            cube.pose.position.x = 0
            cube.pose.position.y = 0
            cube.pose.position.z = 0
            cube.pose.orientation.x = 0
            cube.pose.orientation.y = 0
            cube.pose.orientation.z = 0
            cube.pose.orientation.w = 0
            cube.color.r = 1
            cube.color.g = 1
            cube.color.b = 1
            cube.color.a = 0.3

            arrow_w = entity.arrows.add()
            arrow_w.pose.position.x = a_w.x;
            arrow_w.pose.position.y = a_w.y;
            arrow_w.pose.position.z = a_w.z;





            bool_message = BoolValue()
            bool_message.value = payload.stance  # Example: alternate between True and False
            print("Serialized BoolValue:", bool_message.SerializeToString())

            a_m = Vector3()
            a_m.x = payload.a_m[0]
            a_m.y = payload.a_m[1]
            a_m.z = payload.a_m[2]

            fa = Vector3()
            fa.x = payload.fa[0]
            fa.y = payload.fa[1]
            fa.z = payload.fa[2]

            # await server.send_message(is_stance_id, now, bool_message.SerializeToString())

            # root transforms because foxglove assert
            tfs = FrameTransforms()
            tf = tfs.transforms.add()
            tf.parent_frame_id = "<root>"  # The base or world frame
            tf.child_frame_id = "imu"   # This is okay for a static root frame
            tf.translation.x = payload.p[0]
            tf.translation.y = payload.p[1]
            tf.translation.z = payload.p[2]
            tf.rotation.x = payload.q[1]
            tf.rotation.y = payload.q[2]
            tf.rotation.z = payload.q[3]
            tf.rotation.w = payload.q[0]

            await asyncio.gather(
                server.send_message(tfs_id, now, tfs.SerializeToString()),
                server.send_message(worldview_id, now, scene_update.SerializeToString()),
                server.send_message(a_m_id, now, a_m.SerializeToString()),
                server.send_message(a_w_id, now, a_w.SerializeToString()),
                server.send_message(a_b_id, now, a_b.SerializeToString()),
                server.send_message(fa_id, now, fa.SerializeToString()),
                server.send_message(v_id, now, v.SerializeToString()),
                server.send_message(is_stance_id, now, bool_message.SerializeToString())
            )


if __name__ == "__main__":
    run_cancellable(main())

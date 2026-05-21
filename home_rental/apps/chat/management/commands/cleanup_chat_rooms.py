from django.core.management.base import BaseCommand
from mongoengine.errors import DoesNotExist

from apps.listings.models import ChatRoom


class Command(BaseCommand):
    help = (
        'Detect orphaned chat rooms with missing listing, owner, or tenant references. '
        'Use --delete to remove broken records from MongoDB.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete broken chat rooms instead of only reporting them.',
        )

    def handle(self, *args, **options):
        delete_broken = options['delete']
        rooms = list(ChatRoom.objects.order_by('-last_message_at'))
        broken_rooms = []

        for room in rooms:
            missing = []
            for field_name in ('listing', 'tenant', 'owner'):
                try:
                    getattr(room, field_name)
                except DoesNotExist:
                    missing.append(field_name)
                except Exception:
                    missing.append(field_name)

            if missing:
                broken_rooms.append((room, missing))

        if not broken_rooms:
            self.stdout.write(self.style.SUCCESS('No orphaned or invalid chat rooms found.'))
            return

        self.stdout.write(self.style.WARNING(f'Found {len(broken_rooms)} broken chat room(s):'))
        for room, missing in broken_rooms:
            self.stdout.write(
                f' - room_id={room.id} status={room.status or "unknown"} '
                f'last_message_at={room.last_message_at} missing={",".join(missing)}'
            )

        if delete_broken:
            deleted = 0
            for room, missing in broken_rooms:
                try:
                    room.delete()
                    deleted += 1
                except Exception as exc:
                    self.stderr.write(
                        f'Failed to delete room {room.id}: {exc}'
                    )
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} broken chat room(s).'))
        else:
            self.stdout.write(
                self.style.NOTICE(
                    'Run this command again with --delete to remove broken chat rooms.'
                )
            )

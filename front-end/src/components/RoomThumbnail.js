import { Link } from 'react-router-dom';

const RoomThumbnail = ({
  className,
  roomIndex,
  roomName,
  roomUuid,
  thumbnail = `${process.env.PUBLIC_URL}/images/thumbnail-room-empty.png`,
}) => {
  return (
    <div className={className}>
      <Link to={roomUuid ? `/room/${roomUuid}` : ''}>
        <div className='absolute top-0 left-0 h-8 w-fit bg-amber-500 px-2 text-center font-medium leading-8 text-white opacity-90'>
          {roomIndex}
        </div>
        <img alt={`thumbnail-${roomName}`} src={thumbnail} className='h-full w-full object-cover' />
        <div className='absolute bottom-0 h-8 w-full bg-amber-500 px-3 text-center font-medium leading-8 tracking-wider text-white opacity-90'>
          <p className='overflow-hidden text-ellipsis whitespace-nowrap'>{roomName}</p>
        </div>
      </Link>
    </div>
  );
};

export default RoomThumbnail;

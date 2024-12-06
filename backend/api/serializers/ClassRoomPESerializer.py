from rest_framework import serializers

from api.models import ClassRoomPE, ClassRoom, PeerEval, ClassRoomPETaker


class ClassRoomPESerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoomPE
        fields = ['id', 'peer_eval_id', 'class_id']
        labels = {
            'peer_eval_id': 'Peer Evaluation ID',
            'class_id': 'Class ID'
        }

    def create(self, validated_data):
        peer_eval_id = validated_data.get('peer_eval_id')
        class_id = validated_data.get('class_id')

        # Check if peer_eval_id and class_id exist in the database
        if not ClassRoom.objects.filter(id=class_id).exists():
            raise serializers.ValidationError("Class ID does not exist.")

        if not PeerEval.objects.filter(id=peer_eval_id).exists():
            raise serializers.ValidationError("Peer Evaluation ID does not exist.")

        # Create the instance if both IDs exist
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance
    

class ClassRoomPETakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassRoomPETaker
        fields = ['id', 'class_member_id', 'class_room_pe_id', 'status']
        labels = {
            'class_member_id': 'Class Member ID',
            'class_room_pe_id': 'Class Room PE ID',
            'status': 'Status'
        }

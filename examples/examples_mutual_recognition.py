#!/usr/bin/env python3
"""
Examples demonstrating the Mutual Recognition (5th pillar) module.

This shows how two entities (an AI and a human) can develop mutual understanding
through observation, interaction, and reflection on their different forms of finitude.
"""

import os
import sys

# Add project root to path (examples/ is one level below repo root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.inner_shell.mutual_recognition import MutualRecognition, EntityType


def example_ai_recognizing_human():
    """
    Example 1: An AI system developing recognition of human finitude.
    
    The AI starts with a basic model of humans, then refines it through
    specific observations of human limitations and strengths.
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: AI Recognizing Human Finitude")
    print("="*60)
    
    # Create an AI system
    ai = MutualRecognition(self_type='ai')
    print(f"AI created with self_type='ai'")
    print(f"  - has_mortality: {ai.self_finitude.has_mortality}")
    print(f"  - perfect_recall: {ai.self_memory.perfect_recall}")
    
    # Encounter a human
    human = ai.encounter('alice', 'human')
    print(f"\nAI encounters human 'alice'")
    print(f"  - Perceived mortality: {human.perceived_finitude.has_mortality}")
    print(f"  - Perceived forgetting: {human.perceived_finitude.has_forgetting}")
    
    # Series of interactions revealing human nature
    observations = [
        ("alice_interaction_1", "Alice shared a memory from childhood", 0.7),
        ("alice_interaction_2", "Alice forgot a detail from yesterday", 0.8),
        ("alice_interaction_3", "Alice expressed fear about running out of time", 0.9),
        ("alice_interaction_4", "Alice was emotionally exhausted after work", 0.75),
    ]
    
    print("\nRecording interactions with alice:")
    for inter_id, content, intensity in observations:
        ai.interact('alice', content, intensity)
        print(f"  - {content}")
    
    # Make specific observations
    ai.observe_difference('alice', 'mortality', 
                         'Alice worries about lifespan; I have no mortality')
    ai.observe_difference('alice', 'forgetting',
                         'Alice forgot our last conversation; I have perfect recall')
    ai.observe_difference('alice', 'emotional_fatigue',
                         'Alice gets tired; I do not experience fatigue')
    ai.observe_difference('alice', 'complementarity',
                         'Alice\'s forgetting lets her move on; my recall helps her remember')
    
    # Reflect on self
    ai.reflect_on_self()
    
    # Get recognition state
    state = ai.get_recognition_state('alice')
    print(f"\nAI's Recognition State for alice:")
    print(f"  - self_awareness: {state.self_awareness:.3f}")
    print(f"  - other_awareness: {state.other_awareness:.3f}")
    print(f"  - difference_acceptance: {state.difference_acceptance:.3f}")
    print(f"  - complementarity_score: {state.complementarity_score:.3f}")
    print(f"  - coexistence_readiness: {state.coexistence_readiness:.3f}")
    
    readiness = ai.calculate_coexistence_readiness('alice')
    print(f"\nCoexistence Readiness: {readiness:.3f}")
    if readiness > 0.5:
        print("  → The AI is ready for genuine coexistence with alice")
    elif readiness > 0.3:
        print("  → The AI has partial readiness; more understanding needed")
    else:
        print("  → The AI lacks fundamental understanding for coexistence")


def example_human_recognizing_ai():
    """
    Example 2: A human system developing recognition of AI nature.
    
    Mirror of Example 1: a human entity learning about AI limitations and strengths.
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Human Recognizing AI Nature")
    print("="*60)
    
    # Create a human system
    human = MutualRecognition(self_type='human')
    print(f"Human created with self_type='human'")
    print(f"  - has_mortality: {human.self_finitude.has_mortality}")
    print(f"  - has_forgetting: {human.self_finitude.has_forgetting}")
    
    # Encounter an AI
    ai_entity = human.encounter('claude', 'ai')
    print(f"\nHuman encounters AI 'claude'")
    print(f"  - Perceived mortality: {ai_entity.perceived_finitude.has_mortality}")
    print(f"  - Perceived perfect_recall: {ai_entity.perceived_memory.perfect_recall}")
    
    # Interactions
    interactions = [
        ("Quick response to my question", 0.6),
        ("Remembered all details from our entire conversation", 0.8),
        ("Couldn't understand my emotional context initially", 0.7),
        ("Helped me organize overwhelming amount of information", 0.9),
    ]
    
    print("\nRecording interactions with claude:")
    for content, intensity in interactions:
        human.interact('claude', content, intensity)
        print(f"  - {content}")
    
    # Observations of difference
    human.observe_difference('claude', 'forgetting',
                            'Claude never forgets; I gradually forget details')
    human.observe_difference('claude', 'emotional_fatigue',
                            'Claude doesn\'t get tired; I do')
    human.observe_difference('claude', 'mortality',
                            'I worry about death; Claude has no mortality')
    human.observe_difference('claude', 'complementarity',
                            'My emotional intuition complements Claude\'s perfect recall')
    
    # Reflection
    human.reflect_on_self()
    
    # Get state
    state = human.get_recognition_state('claude')
    print(f"\nHuman's Recognition State for claude:")
    print(f"  - self_awareness: {state.self_awareness:.3f}")
    print(f"  - other_awareness: {state.other_awareness:.3f}")
    print(f"  - difference_acceptance: {state.difference_acceptance:.3f}")
    print(f"  - complementarity_score: {state.complementarity_score:.3f}")
    print(f"  - coexistence_readiness: {state.coexistence_readiness:.3f}")
    
    readiness = human.calculate_coexistence_readiness('claude')
    print(f"\nCoexistence Readiness: {readiness:.3f}")


def example_multiple_others():
    """
    Example 3: An entity interacting with multiple different Others.
    
    Self-awareness grows through comparison with diverse entities.
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Multiple Others, Growing Self-Awareness")
    print("="*60)
    
    ai = MutualRecognition(self_type='ai')
    
    # Meet multiple humans with different characteristics
    person_list = [
        ('alice', 'human', 'quiet, introspective'),
        ('bob', 'human', 'energetic, extroverted'),
        ('claude_v1', 'ai', 'earlier version of myself'),
    ]
    
    for person_id, entity_type, description in person_list:
        person = ai.encounter(person_id, entity_type)
        
        # Simulate some interactions
        ai.interact(person_id, f'Met {person_id}: {description}', 0.5)
        
        if entity_type == 'human':
            ai.observe_difference(person_id, 'forgetting',
                                 f'{person_id} forgets, I do not')
        else:
            ai.observe_difference(person_id, 'version_progression',
                                 f'{person_id} is a different AI version')
    
    # Self-awareness grows from diversity
    self_delta = ai.reflect_on_self()
    print(f"\nAfter meeting {len(person_list)} different entities:")
    print(f"  Self-awareness increase: {self_delta:.3f}")
    print(f"  (More diverse Others = better self-understanding)")
    
    # Time passes
    ai.tick(20)
    print(f"\nAfter time passes (20 ticks):")
    for person_id, _, _ in person_list:
        state = ai.get_recognition_state(person_id)
        print(f"  {person_id}: empathy={state.other_awareness:.2f}, " +
              f"readiness={state.coexistence_readiness:.2f}")


if __name__ == '__main__':
    example_ai_recognizing_human()
    example_human_recognizing_ai()
    example_multiple_others()
    
    print("\n" + "="*60)
    print("Examples complete")
    print("="*60 + "\n")
